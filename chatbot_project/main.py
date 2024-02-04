import web_crawler
import chatbot
import sys

if __name__ == '__main__':
    # Take in a system argument about whether to run the web crawler or not
    web_first = False
    try:
        if sys.argv[1] == "True":
            web_first = True
    except:
        print("No valid system argument passed in.")
    if web_first:
        starter_urls = ["https://www.d20srd.org/index.htm"]
        crawler = web_crawler.WebCrawler(starter_urls)
        # Find URLs from starter URLs provided
        crawler.find_urls()
        print("Found URLs:")
        for url in crawler.urls:
            print(url)
        # Scrape the data from the URLs
        crawler.scrape_all_urls()
        # Clean up found data
        crawler.clean_files()
        # Extract important terms
        crawler.extract_important_terms()
        # Build final knowledge base
        crawler.build_knowledge_base()

