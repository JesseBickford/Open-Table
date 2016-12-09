import pandas as pd
from bs4 import BeautifulSoup
import urllib2
import selenium.webdriver
import re


'''This script by @https://github.com/JesseBickford. This data miner
will extract the first 100 restaurants from Open Table into a csv.'''

restaurantsdf = pd.DataFrame()
url = "http://www.opentable.com/washington-dc-restaurant-listings"

def getrestaurants(url, df):
    driver = selenium.webdriver.PhantomJS()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
    name = []
    location = []
    dailybooked = []
    price = []
    genre = []

    for entry in soup.find_all('div', {'class': 'message-alerts'}):
        if 'Booked' in entry.renderContents():
            reserves = entry.renderContents().strip() #strips html tags
            dailybooked.append(reserves)
        else:
            dailybooked.append(0)
    for entry in soup.find_all('span', {'class': 'rest-row-name-text'}):
        name.append(entry.renderContents())
    for entry in soup.find_all('span', {'class': 'rest-row-meta--location rest-row-meta-text'}):
        location.append(entry.renderContents())
    for entry in soup.find_all('div', {'class': 'rest-row-pricing'}):
        price.append(entry.renderContents().strip())
    for entry in soup.find_all('span', {'class': 'rest-row-meta--cuisine rest-row-meta-text'}):
        genre.append(entry.renderContents())
    data = pd.DataFrame({'Name': name, 'Location': location,'Price': price, 'Type': genre, 'Daily Reservations': dailybooked})
    return data

restaurantsdf = getrestaurants(url, restaurantsdf)     #generates the data frame

'''Clean the data'''
restaurantsdf = restaurantsdf[restaurantsdf['Daily Reservations'] != 0]  #drop the rows with no daily reservations today
restaurantsdf['Daily Reservations'] = [re.search('Booked(.*)times today', num).group(1) for num in restaurantsdf['Daily Reservations']] #Take just the # of bookings
restaurantsdf['Price'] = [re.search('<i>(.*)</i>', price).group(1).count('$') for price in restaurantsdf['Price']] #clean up and make a count of '$'
restaurantsdf['Daily Reservations'] = restaurantsdf['Daily Reservations'].astype(int) #set the type to integer
restaurantsdf['Name'] = [name.replace('amp;', '') for name in restaurantsdf['Name']]


restaurantsdf.sort_values('Daily Reservations', ascending=False) #list restaurants in order of most reservations


restaurantsdf.to_csv('Top100Dc12_7_16.csv', encoding ='utf-8')  #save to CSV
