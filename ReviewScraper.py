from bs4 import BeautifulSoup as soup
import urllib
from urllib.request import urlopen
import ssl
import numpy as np
import pandas as pd
import csv
ssl._create_default_https_context = ssl._create_unverified_context #for some reason urllib thinks the ssl request is expired even though it isn't
global_header= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)' #no idea what this does but you get a 403 error otherwise
          'AppleWebKit/537.11 (KHTML, like Gecko)'
          'Chrome/23.0.1271.64 Safari/537.11',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive'}
def initializeScrape(year, page):
    link = "https://www.metacritic.com/browse/games/score/metascore/year/all/filtered?year_selected={year}&distribution=&sort=desc&view=detailed&page={page}".format(
        year=year, page=page)  # the pages are zero indexed
    req = urllib.request.Request(url=link, headers=global_header)
    pageHTML = urllib.request.urlopen(req).read()
    parsedPage = soup(pageHTML, "html.parser")
    return parsedPage

def getAllLinks(parsedPage):
    retArr = []
    all_links = parsedPage.find_all("a", {"class": "title"})
    for links in all_links:
        retArr.append("https://metacritic.com" + links['href'] + "/critic-reviews")
    return retArr

def getReviewsAndScores(link): #the link is the critic-reviews link for the individual game
    req = urllib.request.Request(url=link, headers=global_header)
    try:
        pageHTML = urllib.request.urlopen(req)
    except Exception:
        return None
    parsedPage = soup(pageHTML, features="lxml")
    reviews_section = parsedPage.find("div", {"class":"body product_reviews"})
    if reviews_section is None:
        print("Got here")
        return None
    indiv_reviews_score = reviews_section.find_all("div", {"class":"review_section"})
    retArr = []
    for reviews in indiv_reviews_score:
        review_body = reviews.find("div", {"class":"review_body"})
        review_score = reviews.find("div", {"class":"review_grade"})
        if review_body is not None and review_score is not None:
            retArr.append([review_body.text.strip(), int(review_score.find("div").text)])
    return retArr

def getReviewsForLinks(allLinks): #takes in all of the critic reviews for all the games on one page
    retArr = []
    for links in allLinks:
        print(links)
        review = getReviewsAndScores(links)
        if review is not None:
            retArr.extend(review)
    return retArr

def getAllReviews(year, noOfPages):
    retArr = []
    for i in range(noOfPages):
        print("I am now on page " + str(i + 1))
        parsedPage = initializeScrape(year, i)
        allLinks = getAllLinks(parsedPage)
        allReviewsOnPage = getReviewsForLinks(allLinks)
        retArr.extend(allReviewsOnPage)
    return np.array(retArr)

def main():
    arr = []
    # arr2017 = getAllReviews(2017, 11)
    # arr2018 = getAllReviews(2018, 12)
    arr2019 = getAllReviews(2019, 11)
    # arr2020 = getAllReviews(2020, 11)
    # arr.extend(arr2019)
    # arr.extend(arr2018)
    # arr.extend(arr2019)
    # arr.extend(arr2020)
    df = pd.DataFrame(arr2019, columns=['Review', 'Score'])
    df.to_csv("data2019.csv", index=False)
    # with open("data3.csv", "w+", newline='', encoding="utf-8") as my_csv:
    #     csvWriter = csv.writer(my_csv, delimiter=',')
    #     csvWriter.writerows(retArr)


if __name__ == "__main__":
    main()