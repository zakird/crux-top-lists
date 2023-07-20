import argparse

from downloader import CrUXRepoManager


def main(directory, credentials_path):
    mgr = CrUXRepoManager(directory)
    credentials_env = None if credentials_path else True
    mgr.download(credentials_path, credentials_env=credentials_env)
    mgr.update_current("current.csv.gz")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='cruxdownloader',
        description='Download CrUX top lists aggregated by month',
    )
    parser.add_argument('directory', required=True)
    parser.add_argument('--credential-file', default=None)
    args = parser.parse_args()
    main(args.directory, args.credential_file)
