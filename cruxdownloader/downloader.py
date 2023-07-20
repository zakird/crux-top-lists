import json
import sys
import os
import dateutil
from dateutil import rrule
import dateutil.relativedelta as relativedelta
import datetime
import gzip
import shutil

from google.cloud import bigquery
from google.oauth2 import service_account


class CrUXDownloader:

    GLOBAL_SQL = """SELECT distinct origin, experimental.popularity.rank
        FROM `chrome-ux-report.experimental.global`
        WHERE yyyymm = ? AND experimental.popularity.rank <= 1000000
        GROUP BY origin, experimental.popularity.rank
        ORDER BY experimental.popularity.rank;"""

    COUNTRY_SQL = """SELECT distinct country_code, origin, experimental.popularity.rank
        FROM `chrome-ux-report.experimental.country`
        WHERE yyyymm = ? AND experimental.popularity.rank <= 1000000
        GROUP BY country_code, origin, experimental.popularity.rank
        ORDER BY country_code, experimental.popularity.rank;"""

    def __init__(self, credentials_path=None, credentials_json=None, credentials_env=False):
        if not credentials_path and not credentials_json and not credentials_env:
            raise Exception("No credentials supplied for Google Cloud")
        if credentials_env:
            self._bq_client = bigquery.Client()
        elif credentials_json:
            obj = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(obj)
            self._bq_client = bigquery.Client(credentials=credentials)
        else:
            self._bq_client = bigquery.Client.from_service_account_json(credentials_path)

    def dump_month_to_csv(self, scope, yyyymm: int, path):
        assert scope in {"global", "country"}
        query = self.GLOBAL_SQL if scope == "global" else self.COUNTRY_SQL
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(None, "INT64", yyyymm),
            ]
        )
        df = self._bq_client.query(query, job_config=job_config).to_dataframe()
        if df.empty:
            return
        df.to_csv(path, index=False, header=True)
        return path


class CrUXRepoManager:

    MIN_YYYYMM = datetime.datetime(2021, 2, 1)
    GLOBAL_DIR_NAME = "global"
    COUNTRY_DIR_NAME = "country"

    @classmethod
    def _iter_valid_YYYYMM(cls):
        now = datetime.datetime.now()
        last_month = now + relativedelta.relativedelta(months=-1)
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=cls.MIN_YYYYMM,
                until=last_month):
            yield (dt.year, dt.month)

    def __init__(self, data_directory):
        self._data_directory = data_directory
        self._global_directory = os.path.join(data_directory,
                self.GLOBAL_DIR_NAME)
        self._country_directory = os.path.join(data_directory,
                self.COUNTRY_DIR_NAME)

    def _get_existing_YYYYMM(self, path):
        for f in os.listdir(path):
            if not f.startswith("2"):
                continue
            yield int(f[0:4]), int(f[4:6])

    def _to_fetch_YYYYMM(self, path):
        valid = set(self._iter_valid_YYYYMM())
        existing = set(self._get_existing_YYYYMM(path))
        for dt in valid - existing:
            mm = str(dt[1])
            if len(mm) == 1:
                mm = "0" + mm
            yield int(str(dt[0]) + mm)

    def _make_directories(self):
        if not os.path.exists(self._global_directory):
            os.mkdir(self._global_directory)
        if not os.path.exists(self._country_directory):
            os.mkdir(self._country_directory)

    def _gzip(self, filename, delete_original=True):
        with open(filename, 'rb') as f_in:
            gzipped_filename = filename + ".gz"
            with gzip.open(gzipped_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        if delete_original:
           os.remove(filename)

    def download(self, credentials_path=None, credentials_json=None, credentials_env=False):
        downloader = CrUXDownloader(
            credentials_path=credentials_path,
            credentials_json=credentials_json,
            credentials_env=credentials_env,
        )
        self._make_directories()
        for scope in {"global",}:
        #for scope in {"global", "country"}:
            data_directory = self._global_directory if scope == "global" else self._country_directory
            for yyyymm in self._to_fetch_YYYYMM(data_directory):
                print("Fetching {} {}".format(scope, yyyymm))
                filename = str(yyyymm) + ".csv"
                results_path = os.path.join(data_directory, filename)
                if downloader.dump_month_to_csv(scope, yyyymm, results_path):
                    self._gzip(results_path)

    def update_current(self, dest):
        # Global Only right now
        latest = max(self._get_existing_YYYYMM(self._global_directory))
        latest_filename = str(latest[0]) + str(latest[1]).zfill(2) + ".csv.gz"
        src_path = os.path.join(self._global_directory, latest_filename)
        assert(os.path.exists(src_path))
        dst_path = os.path.join(self._global_directory, dest)
        shutil.copyfile(src_path, dst_path)

