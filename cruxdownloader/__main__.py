from downloader import CrUXRepoManager

def main():
    #CrUXDownloader("credentials.json").dump_month_to_csv("country", 202211, "test")
    CrUXRepoManager("data").run("credentials.json")

if __name__ == "__main__":
    main()
