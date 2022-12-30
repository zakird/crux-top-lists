import sys

from downloader import CrUXRepoManager

def main(directory, credentials_path):
    #CrUXDownloader("credentials.json").dump_month_to_csv("country", 202211, "test")
    mgr = CrUXRepoManager(directory)
    mgr.download(credentials_path)
    mgr.update_current("current.csv.gz")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
