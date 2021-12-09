# HWZ Scraper


## Introduction

The script in this repository serves as a way to scrape comments from HardwareZone (HWZ) forums. 

While much progress has been made in the field of Natural Language Processing, little work has been done to study relationships between informal languages and formal languages. This repository aims to bridge the gap between informal and formal language by scraping data from HardwareZone Forums which can be treated as Singlish (Singaporean-English) data. The data can then be further processed for other uses (Data Analysis, Machine Translation etc.) The purpose of this repository is strictly for academic purpose and not for commerical usage.

## How does the code work?

### External libraries used

- bs4 (Scraping)
- requests (Scraping) 
- re (Regex - Cleaning)

### Scraping method

A single HWZ forum consists of multiple pages of threads. Each page of thread consists of multiple threads. Each thread consists of multiple pages of comments. Each page of comment consists of multiple comments.

The code is simply a nested loop which will continue scraping the forum until the **target** number of comments have been scraped. 

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
thread: link to the thread, default = "https://forums.hardwarezone.com.sg/forums/eat-drink-man-woman.16"
target-number: target number of comments to scrape, default = 10000
max-per-thread: maximum number of comments per thread, default = 1000. This helps to increase variability in the data
scrape-type: whether the output is by comments or split into sentences

## To do
1. Multi threading to increase speed of scraping
2. Adding more optional arguments
3. Add in link to Kaggle notebook
