#----------------IMPORTS---------------------------------
from googlesearch import search
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
from sqlalchemy import create_engine
from datetime import datetime

print('Imports done.')

text_excerpts=pd.DataFrame()
opened_urls=[]
successful_urls=[]
i=0
j=0
search_phrase = "footprint"

#----------FUNCTIONS----------------

def google_search(query):
    found=[]
    #appending each url that is found as a result for the given query to a dataframe
    for url in search(query,stop=10, tld='com', lang='en', pause=2.0):
        found.append(url)
    df_found=pd.DataFrame(found)
    #adding timestamp, status and query phrase to the url dataframe
    df_found['Timestamp']=pd.Timestamp.now()
    df_found['Timestamp'] = df_found['Timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    df_found['Status']= 'FOUND'
    df_found['Search Phrase']= query
    df_found['Process State']=0
    #changing column names of dataframe
    df_found.columns=['URL','Timestamp','Status','Search Phrase', 'Process State']
    #found_to_sql
    return df_found

def found_to_sql(dataframe):
    engine = create_engine("mysql+pymysql://{user}:{pw}@localhost:{port}/{db}"
                       .format(user="root",
                               pw='',
                               db="zoe2",
                               port="3306"))
    # engine = create_engine("mysql+pymysql://{user}:{pw}@localhost:{port}/{db}"
    #                    .format(user="root",
    #                            pw='Z20e0ne54n+27',
    #                            db="cft",
    #                            port="3306"))
    conn= engine.connect()
    conn.close()
    dataframe.to_sql('found', con = engine, if_exists = "append", index=False)


def scrape_text(url):
    # checking if the url is a pdf
    '''load df_found'''
    if url.endswith('pdf') == True:
        print('PDF cannot be scraped.')
    else:
        # checking if we already opened the url
        if url not in opened_urls:
            global i
            # counting the URLs we opened
            print('Opening URL' + str(i))
            # opening URL
            r = requests.get(url)
            # adding url to our list of opened urls
            opened_urls.append(url)
            # retrieving html text from website
            response = r.text
            soup = BeautifulSoup(response)
            # getting pure text out of html text
            text = soup.get_text()
            print('GOT TEXT.')
            # calling function to extract words
            text_excerpts=find_words(text, search_phrase , url)            
            i += 1
            # appending extracted texts to our python dataframe, text_excerpts is basically the populated df
    return text_excerpts


def find_words(text, search_phrase, url):
    # making website text all lower case and splitting it into a list of words
    '''if x in text, get index number of x'''
    text_list = text.lower().split()
    print('SEARCHING KEY WORDS.')
    index_list = []
    excerpts = []
    # getting index number of words that match search phrase results
    for index, elem in enumerate(text_list):
        # print(text_list)
        if elem == search_phrase:
            # print(f"{search_phrase} is found at index {index}")
            index_list.append(index)
        else:
            continue

    print(str(search_phrase) + " found " + str(len(index_list)) + " times.")
    if len(index_list) > 0:
        successful_urls.append(url)
        # checking if search phrase was found in the text
    for i in index_list:
        # index_list is started anew for each url. This makes sure the search phrase was found at all.
        # scraping 100 words left&right from search phrase
        text100 = text_list[(i - 100):(i + 100)]
        if text100 != "" or " " or "''":
            excerpts.append(" ".join(text100))

        else:
            continue
            # print('Search Phrase not found.')
    # turning results into a dataframe
    df_excerpts = pd.DataFrame(excerpts)
    df_excerpts['Timestamp'] = pd.Timestamp.now()
    df_excerpts['Status'] = 'POPULATED'
    df_excerpts['Search Phrase'] = search_phrase
    df_excerpts = df_excerpts.rename({0: "Text"}, axis='columns')
    df_excerpts["Url"] = url
    text_excerpts = df_excerpts.rename({0: "Text"}, axis='columns')
    # text_excerpts["Url"] = url
    text_excerpts.append(df_excerpts)
    # calling function to write new text excerpts to sql database
    #populated_to_sql(df_excerpts)
    return text_excerpts, successful_urls

# google_search('Carbon Footprint')
# print('Search Done.')
# df=google_search('flask')
# df['URL'][0:5].apply(scrape_text)