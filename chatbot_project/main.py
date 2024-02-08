import web_crawler
import chatbot
import sys
import os

if __name__ == '__main__':
    # Take in a system argument about whether to run the web crawler or not
    web_first = False
    try:
        if sys.argv[1] == "True":
            web_first = True
    except:
        print("No valid system argument passed in.")
    if web_first:
        starter_urls = ["https://www.d20srd.org/indexes/basicsRacesDescription.htm",
                        "https://www.d20srd.org/indexes/classes.htm",
                        "https://www.d20srd.org/indexes/skills.htm",
                        "https://www.d20srd.org/srd/feats.htm"]
        crawler = web_crawler.WebCrawler(starter_urls)
        # Find URLs from starter URLs provided
        if not crawler.urls:
            crawler.find_urls()
        # Scrape the data from the URLs
        files = os.listdir("files/raw_information")
        if len(files) == 0:
            crawler.scrape_all_urls()
        # Clean up found data
        clean_files = os.listdir("files/clean_information")
        if len(clean_files) == 0:
            crawler.clean_files()
        # Extract important terms
        if not crawler.terms:
            crawler.extract_important_terms()
        # Build final knowledge base
        crawler.build_knowledge_base()

    adamant = chatbot.Chatbot()

