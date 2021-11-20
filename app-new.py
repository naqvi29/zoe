from re import I
from typing import final
from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from Functions import google_search, found_to_sql, scrape_text, find_words
import json
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')    

@app.route('/search',methods=['POST'])
def search():    
    searchphrase = request.form['searchphrase']    
    # search_results= google_search(searchphrase)
    # df = search_results["URL"][0:5].apply(scrape_text)
    # read from populated excel file 
    df = pd.read_excel('populated.xlsx')
    print (df) 
    df_json = df.to_json(orient='records')
    results = json.loads(df_json)

    # get no of items for results.html 
    number_of_items = len(results)
    return render_template('results.html',number_of_items=number_of_items, phrase=searchphrase, results=results)

@app.route('/save', methods=['POST'])
def save():
    results = request.form.get('results')
    
    select_all = request.form.get('select_all')
    # load the json instance returned
    data_json = json.loads(results)
    with open('data2.json', 'w', encoding='utf-8') as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)
    
    # convert it to data frame
    df = pd.json_normalize(data_json)
    
    totalResults = len(data_json)
    i = 0
    checkboxes = []
    for i in range(totalResults):  
        select = request.form.get(str(i))
        i = i+1
        checkboxes.append(select)
    selected = []
    for val in checkboxes:
        if val != None :
            selected.append(val)    
    # assign column names
    df.columns = ["Process State","Search Phrase","Status","Text", "Timestamp",
                  "URL", "Unnamed: 0"]
    # if user checks all boxes
    if select_all == 'all':
        found_to_sql(df)
        return render_template('commited.html',status="All Results Commited")
    # if user check selected boxes 
    elif select_all == None:
        # now convert string in list to integers
        selected_boxes = [int(x) for x in selected]
        rows = selected_boxes
        df = df.loc[rows]
        # Commit to database
        found_to_sql(df)
        # return ("Selected Data Saved")
        return render_template('commited.html',status="Selected Results Commited")


if __name__ == '__main__':
    app.debug = True
    app.run()