from bs4 import BeautifulSoup
from requests import get
import re
import argparse
import time
import concurrent.futures


def obtain_max_pages(html_soup):
    page_nums = html_soup.find_all('ul', class_ = 'pageNav-main')
    if page_nums == []:
        return 1
    else:
        return page_nums[0].find_all('li')[-1].text


def obtain_all_threads(url):
    print("Start - Scraping URLS of threads of interest")
    start = time.time()
    all_threads = []
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    max_pages = obtain_max_pages(html_soup)
    max_pages = int(max_pages)
    
    summary = html_soup.find_all('div', class_="structItem-title")
    urls = [url + "/page-" +  str(page) for page in range(1,max_pages+1)]
    
    def scrape_forum_page(url):
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        summary = html_soup.find_all('div', class_="structItem-title")
        for article in summary:
            thread_url = "https://forums.hardwarezone.com.sg"+article.find('a')['href']
            all_threads.append(thread_url)
        return
        
    print(urls[0:10])
    print(len(urls))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(scrape_forum_page, url): url for url in urls}
        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            completed += 1
            if completed % 100 == 0:
                print("Progress:", completed * 100 / max_pages, "%")

    print("Completed - Scraped URLs of threads of interest")
    print("Time taken:", time.time() - start)

    return list(dict.fromkeys(all_threads))



def main():
    parser = argparse.ArgumentParser(description = "Inputs to HWZ Scraper")
    parser.add_argument('--thread', type=str, default = "https://forums.hardwarezone.com.sg/forums/eat-drink-man-woman.16", help = "thread to scrape")

    args = parser.parse_args()

    thread_urls = obtain_all_threads(args.thread)
    textfile = open("thread_urls.txt", "w", encoding='utf-8')
    for element in thread_urls:
       textfile.write(element + "\n")


if __name__ == '__main__':
    main()


