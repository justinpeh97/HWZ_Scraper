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


def obtain_all_threads(url, target_num_threads):
    print("Start - Scraping URLS of threads of interest")
    all_threads = []
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    max_pages = obtain_max_pages(html_soup)
    summary = html_soup.find_all('div', class_="structItem-title")
    num_pages = int(((target_num_threads // 20 )+1) * 1.1)
    urls = [url + "/page-" +  str(page) for page in range(1,num_pages)]
    
    def scrape_forum_page(url):
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        summary = html_soup.find_all('div', class_="structItem-title")
        for article in summary:
            thread_url = "https://forums.hardwarezone.com.sg"+article.find('a')['href']
            all_threads.append(thread_url)
        return
            
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrape_forum_page, urls)

    print("Completed - Scraped URLs of threads of interest")

    return list(dict.fromkeys(all_threads))[:target_num_threads]

def scrape_hwz(url, target_num_threads = 100, max_per_thread = 1000):
    start = time.time()
    def comments_from_thread(url, max_per_thread):
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        max_pages = obtain_max_pages(html_soup) if int(obtain_max_pages(html_soup)) < max_per_thread // 20 else max_per_thread // 20
        pages = [url + "page-" + str(page) for page in range(1, int(max_pages)+1)]
        for page in pages:
            response = get(page)
            html_soup = BeautifulSoup(response.text,'html.parser')
            for soup in html_soup.find_all("div", class_ = "bbWrapper"):
                comment = soup.text
                comment = re.sub('[\n|\t]+',".",comment)
                all_comments.append(comment)
        return 
    
    all_comments = []
    all_threads = obtain_all_threads(url, target_num_threads)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(comments_from_thread, thread, max_per_thread): thread for thread in all_threads}
        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            completed += 1
            if completed % 10 == 0:
                print("Progress:", completed * 100 / target_num_threads, "%")

    print("Time taken:", time.time() - start)
    return all_comments

def clean_comments(comments):
    cleaned_comments = []
    for comment in comments:
        while "Click to expand...." in comment:
            pos = re.search("Click to expand....",comment)
            comment = comment[(pos.span()[1]):]
        if "Sent from" in comment:
            pos = re.search("Sent from",comment)
            comment = comment[:(pos.span()[0])]
        if "Posted from" in comment:
            pos = re.search("Posted from",comment)
            comment = comment[:(pos.span()[0])]
        if re.search(u'[\u4e00-\u9fff]', comment):
            continue
        if "lightbox_close" in comment:
            continue
        if "www." in comment or "http" in comment or ".com" in comment:
            continue
        if len(comment) > 100000:
            continue

        cleaned_comments.append(comment)

    return cleaned_comments

def custom_splitting(comments,symbol):
    output = []
    for comment in comments:
        if symbol in comment:
            comment_split = comment.split(symbol)
            for index in range(len(comment_split)-1):
                comment_split[index] += symbol
            output.extend(comment_split)
        else:
            output.append(comment)
    return output

def convert_to_sentences(comments):
    all_sentences = custom_splitting(comments, ".") # Split by "."
    all_sentences = custom_splitting(all_sentences, "!") # Split by "!"
    all_sentences = custom_splitting(all_sentences, "?") # Split by "?"
    return all_sentences

def percentage_alphabets(sentence):
    len_sent = len(sentence)
    num_alpha = 0
    for char in sentence:
        if char.isalpha() or char == " ":
            num_alpha += 1
    return num_alpha / len_sent

def clean_sentences(sentences):
    cleaned_sentences = []
    for sentence in sentences:
        if len(sentence) < 15 or len(sentence.split()) < 3 or percentage_alphabets(sentence) < 0.75:
            continue
        if sentence[0] == ' ':
            sentence = sentence[1:]
        cleaned_sentences.append(sentence)

    return list(dict.fromkeys(cleaned_sentences))


def main():
    parser = argparse.ArgumentParser(description = "Inputs to HWZ Scraper")
    parser.add_argument('--thread', type=str, default = "https://forums.hardwarezone.com.sg/forums/eat-drink-man-woman.16", help = "thread to scrape")
    parser.add_argument('--num-threads', type=int, default = 50, help='number of threads to scrape')
    parser.add_argument('--max-per-thread', type=int, default = 100, help='maximum number of comments from each thread')

    args = parser.parse_args()

    all_comments = scrape_hwz(args.thread, args.num_threads, args.max_per_thread)
    textfile = open("comments.txt", "w", encoding='utf-8')
    for element in all_comments:
       textfile.write(element + "\n")

    comments_cleaned = clean_comments(all_comments)
    sentences = convert_to_sentences(comments_cleaned)
    cleaned_sentences = clean_sentences(sentences)
    textfile = open("cleaned_sentences.txt", "w", encoding='utf-8')
    for element in cleaned_sentences:
       textfile.write(element + "\n")


if __name__ == '__main__':
    main()


