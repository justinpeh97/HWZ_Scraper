from bs4 import BeautifulSoup
from requests import get
import re
import argparse

def obtain_max_pages(html_soup):
    page_nums = html_soup.find_all('ul', class_ = 'pageNav-main')
    if page_nums == []:
        return 1
    else:
        return page_nums[0].find_all('li')[-1].text

def scrape_forum_page(url, target_num_comments, max_comments_per_thread):
    all_comments = []
    all_threads = []
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    max_pages = obtain_max_pages(html_soup)
    summary = html_soup.find_all('div', class_="structItem-title")

    # Obtain comments for pages of threads
    for page in range(1, int(max_pages)+1):
        url = "https://forums.hardwarezone.com.sg/forums/eat-drink-man-woman.16/" + "page-" + str(page)
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        summary = html_soup.find_all('div', class_="structItem-title")

    
        # Obtain comments for a page of threads
        for article in summary:
            num_comments_in_thread = 0

            # Obtain comments for a single thread

            thread_url = "https://forums.hardwarezone.com.sg"+article.find('a')['href']
            print("https://forums.hardwarezone.com.sg"+article.find('a')['href'])
            if thread_url in all_threads:
                print("Thread already scraped. Exiting thread")
                continue
            else:
                all_threads.append(thread_url)
            response = get(thread_url)
            html_soup = BeautifulSoup(response.text, 'html.parser')
            max_pages = obtain_max_pages(html_soup)

              
            for page in range(1,int(max_pages)+1):
                
                # Obtain all comments for a single page in a thread
                # If the number of comments from a single thread exceeds a certain amount, skip that thread (to increase variability)
                if num_comments_in_thread > max_comments_per_thread:
                  print("Reached maximum number of comments per thread. Exiting thread.")
                  break

                page_url = thread_url + "page" + "-" + str(page)
                response = get(page_url)
                html_soup = BeautifulSoup(response.text, 'html.parser')

                for soup in html_soup.find_all("div", class_ = "bbWrapper"):
                    num_comments_in_thread += 1
                    if len(all_comments) % 1000 == 0:
                        print(len(all_comments)* 100/target_num_comments,"%")
                    if len(all_comments) == target_num_comments:
                        return all_comments
                    comment = soup.text
                    comment = re.sub('[\n|\t]+',".",comment)
                    all_comments.append(comment)

    return all_comments

def clean_comments(comments):
    cleaned_comments = []
    for comment in comments:

        # 1. Get rid of "Click to expand"
        while "Click to expand...." in comment:
            pos = re.search("Click to expand....",comment)
            comment = comment[(pos.span()[1]):]
        
        #2. Get rid of "Sent from ..", "Posted from .."
        if "Sent from" in comment:
            pos = re.search("Sent from",comment)
            comment = comment[:(pos.span()[0])]
        if "Posted from" in comment:
            pos = re.search("Posted from",comment)
            comment = comment[:(pos.span()[0])]

        #3. Get rid of comments containing Chinese characters
        if re.search(u'[\u4e00-\u9fff]', comment):
            continue

        #4. Get rid of comments containing error messages
        if "lightbox_close" in comment:
            continue

        #5. Get rid of comments containing web links
        if "www." in comment or "http" in comment or ".com" in comment:
            continue

        #6. Get rid of super long comments. These are probably errors
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

    # Assume that the only sentence ending punctuations are ., ! or ? and split based on these punctuations
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
        
        # 3 Criterias to keep the sentence
        if len(sentence) < 15 or len(sentence.split()) < 3 or percentage_alphabets(sentence) < 0.75:
            continue
        if sentence[0] == ' ':
            sentence = sentence[1:]
        cleaned_sentences.append(sentence)
    return cleaned_sentences


# The input to the function
# 1. Forum of interest
# 2. Target number of comments
# 3. Maximum number of comments per thread

def main():
    parser = argparse.ArgumentParser(description = "Inputs to HWZ Scraper")
    parser.add_argument('--thread', type=str, default = "https://forums.hardwarezone.com.sg/forums/eat-drink-man-woman.16", help = "thread to scrape")
    parser.add_argument('--target-number', type=int, default = 10000, help='target number of comments/sentences to scrape')
    parser.add_argument('--max_per-thread', type=int, default = 1000, help='maximum number of comments from each thread')
    parser.add_argument('--scrape-type', choices=['comments','sentences'], default='sentences', help="Scrape comments or sentences")

    args = parser.parse_args()

    comments = scrape_forum_page(args.thread, args.target_number, args.max_per_thread)
    comments_cleaned = clean_comments(comments)

    if args.scrape_type == 'comments':
        textfile = open("cleaned_comments.txt", "w", encoding='utf-8')
        for element in comments_cleaned:
           textfile.write(element + "\n")
    else:
        sentences = convert_to_sentences(comments_cleaned)
        cleaned_sentences = clean_sentences(sentences)
        textfile = open("cleaned_sentences.txt", "w", encoding='utf-8')
        for element in cleaned_sentences:
           textfile.write(element + "\n")


if __name__ == '__main__':
    main()
    

