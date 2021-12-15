# HWZ Scraper


## Introduction

The script in this repository serves as a way to scrape comments from HardwareZone (HWZ) forums. 

While much progress has been made in the field of Natural Language Processing, little work has been done to study relationships between informal languages and formal languages. This repository aims to bridge the gap between informal and formal language by scraping data from HardwareZone Forums which can be treated as Singlish (Singaporean-English) data. The data can then be further processed for other uses (Data Analysis, Machine Translation etc.) This repository is strictly for academic purpose and not for commerical usage.

## How does the code work?

### External libraries used

- bs4 (Scraping)
- requests (Scraping) 
- re (Regex - Cleaning)

### Scraping method

To run the code, simply specify the number of threads that you wish to scrape. Lets call this number of threads k. The script will first obtain the URLs of the k most recent  threads. Using the concurrent.futures module, the script utilizes multi-threading to scrape the comments from the k threads. To increase variability in data, the script limits the number of comments per thread to 1000. This can be adjusted by specifying the max-per-thread argument.

### Cleaning

Raw scraped comments are often dirty and hard to read. The following are some cleaning techniques applied to the comments
1. Removing white spaces
2. Removing part of comment which is a quotation of another comment 
3. Removing "Sent from .. " or "Posted from .. "
4. Remove comments containing Chinese characters
5. Remove comments containing links
6. Removing extremely long comments (likely to be errors)

If "sentence" is chosen instead of "comment", we will choose sentences with
1. at least 15 characters
2. at least 3 words
3. alphabets making up at least 75% of the string (excluding white spaces such as " ")

## How to run the code?

To run the code, simply run the following command

````
python scraping.py
````

Additional arguments
- thread: link to the thread, default = "https://forums.hardwarezone.com.sg/forums/eat-drink-man-woman.16"
- num-threads: number of threads to scrape, default = 100
- max-per-thread: maximum number of comments per thread, default = 1000. 
- scrape-type: whether the output is by comments or split into sentences

