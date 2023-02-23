import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re
import pandas as pd
from datetime import date, timedelta, datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
import random
import time
import mysql.connector

#This section connects your database source. For my use case, mySQL was the selection of choice.

#connection created
mydb = mysql.connector.connect(
  host="INSERT HOST NAME",
  user="INSERT USERNAME",
  password="INSERT PASSWORD",
  database="INSERT DATABASE NAME"
)

mycursor = mydb.cursor()

#Input your Discord credentials to connect to your channel webhook.
#Note - Multiple webhooks can be inserted, just copy and paste the original value below.
groups = {
    'INSERT BOT NAME': {
        'name': 'INSERT BOT NAME',
        'color': 'INSERT HEX COLOR',
        'webhook': 'INSERT DISCORD WEBHOOK'},
}

#Generates current timestamp
def get_timestamp():
    today_current = datetime.now()
    current_timestamp = today_current.strftime("%Y-%m-%d %I:%M:%S %p")
    return current_timestamp

#Scrapes Cash App Sitemap URLs
def sitemap(url_list):
    url = 'https://cash.app/sitemap.xml'

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'xml')

    legal_list = []

    for i in soup.find_all('url'):

        #Checks each URL it matches proper syntax
        req = 'https://cash.app/legal/'

        loc = i.find('loc').text.lower()
        loc_split = len(loc.split(req)) #matching output should have length of 2

        if loc_split == 2:
            #Add any new URL links from the Sitemap if not contained in the database from the mySQL query.
            if loc not in url_list:
                legal_list.append(loc)
                send_ping(loc,discord_time(get_begin_time(loc))[0],discord_time(get_begin_time(loc))[1])
                time.sleep(random.randint(1,5))


def send_ping(url, unix_timestamp, timestamp):
    
    
    if unix_timestamp != 0:
        if timestamp != 1:
            
            #This logic only occurs if a timestamp is available.
            ca_dict = []
            
            #Scrapes each new URL link to get the title, url, and event timestamps.
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'lxml')

            rules = soup.find('title').text
            user_title = rules.split('Official Rules')[0].strip()
            
            #Transform all captured data into a dictionary.
            ca_list = {
                'rules_title': rules,
                'user_title': user_title,
                'url': url,
                'unix_timestamp': unix_timestamp,
                'event_timestamp': timestamp,
                'created_at': datetime.now(),
            }

            #Inserts all the captured data into the mySQL database with a tablename called cashapp.
            sql_insert = "INSERT INTO cashapp (rules_title, user_title, url, unix_timestamp, event_timestamp, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
            sql_values = (ca_list['rules_title'], ca_list['user_title'], ca_list['url'], ca_list['unix_timestamp'], ca_list['event_timestamp'], ca_list['created_at'])
            mycursor.execute(sql_insert, sql_values)

            ca_dict.append(ca_list)
            
            #Transforms the dictionary into a pandas dataframe.
            ca_df = pd.DataFrame(ca_dict)

            #Iterates through the pandas dataframe and discord webhooks.
          
            for i in range(0, len(ca_df)):
                for z in groups.values():
                  
                    #Takes each Discord object and inserts into the following parameters.
                    name = z['name']
                    color = z['color']
                    webhook = z['webhook']

                    twitter = 'https://twitter.com/CashApp'
                    instagram = 'https://www.instagram.com/cashapp/?hl=en'

                    webhook_name = DiscordWebhook(url=webhook, username=name)
                    embed = DiscordEmbed(title="New Cashapp Promotion Posted - {}!".format(ca_df['user_title'][i]),description='[{}]({})\n\n**Promotion Start Period:** {}'.format(ca_df['rules_title'][i],url, unix_timestamp),color=color)
                    
                    embed.add_embed_field(name="Cashapp Profiles",value='[Twitter]({}) | [Instagram]({})'.format(twitter,instagram),inline=True)
                    embed.set_timestamp()
                    webhook_name.add_embed(embed)
                    
                    #Webhook is sent of the new job posting.
                    response = webhook_name.execute(remove_embeds=True)
                    
                    #Sleeping to prevent Discord rate limit of 50 messages every 15 second interval.
                    time.sleep(1)
    else:
        #If the event has no timestamp, this logic takes place.
        try:
            ca_dict = []

            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'lxml')

            rules = soup.find('title').text
            user_title = rules.split('Official Rules')[0].strip()

            #Transform all captured data into a dictionary.
            ca_list = {
                'rules_title': rules,
                'user_title': user_title,
                'url': url,
                'unix_timestamp': '',
                'event_timestamp': '',
                'created_at': datetime.now(),
            }
            
            #Inserts all the captured data into the mySQL database with a tablename called cashapp.
            sql_insert = "INSERT INTO cashapp (rules_title, user_title, url, unix_timestamp, event_timestamp, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
            sql_values = (ca_list['rules_title'], ca_list['user_title'], ca_list['url'], ca_list['unix_timestamp'], ca_list['event_timestamp'], ca_list['created_at'])
            mycursor.execute(sql_insert, sql_values)

            ca_dict.append(ca_list)
            ca_df = pd.DataFrame(ca_dict)
            for i in range(0, len(ca_df)):

                for z in groups.values():
                  
                    #Takes each Discord object and inserts into the following parameters.
                    name = z['name']
                    color = z['color']
                    webhook = z['webhook']

                    twitter = 'https://twitter.com/CashApp'
                    instagram = 'https://www.instagram.com/cashapp/?hl=en'

                    webhook_name = DiscordWebhook(url=webhook, username=name)

                    embed = DiscordEmbed(title="New Cashapp Promotion Posted - {}!".format(ca_df['user_title'][i]),description='[{}]({})'.format(ca_df['rules_title'][i], url), color=color)

                    embed.add_embed_field(name="Cashapp Profiles",value='[Twitter]({}) | [Instagram]({})'.format(twitter, instagram), inline=True)
                    embed.set_timestamp()
                    webhook_name.add_embed(embed)
                    
                    #Webhook is sent of the new job posting.
                    response = webhook_name.execute(remove_embeds=True)

                    #Sleeping to prevent Discord rate limit of 50 messages every 15 second interval.
                    time.sleep(1)
        except:
            pass

#Converts timestamp syntax into unix timestamp.
def discord_time(convert_time):
    if convert_time == 0:
        #unix_timestmap = 0
        #timestamp = 1
        return [0, 1]
    else:
        convert_time = convert_time + timedelta(hours=8)
        unix_time = int(time.mktime(convert_time.timetuple()))
        relative_time = '<t:{}:R>'.format(unix_time)
        long_date = '<t:{}:F>'.format(unix_time)
        return [long_date, convert_time]

#Searches the new URL webpage and attempts to locate a timestamp.
def get_begin_time(url):
    time.sleep(random.randint(1,5))

    page = requests.get(url)
    session = HTMLSession()
    response = requests.get(url)
    raw_url = response.url
    r = session.get(raw_url)

    try:
        b = r.html.search('The “Sweepstakes Period” begins at {} on {} and')[0:]
        
        #Regex to find a timestamp pattern.
        time_str = re.findall(r'(\d*\d*:*\d*\d (PM|AM))', b[0])

        date_str = b[1]
        combined_time = date_str + ' ' + time_str[0][0]

        #Pacific Timezone
        try:
            convert_time = datetime.strptime(combined_time, '%B %d, %Y %I:%M %p') 
        except:
            convert_time = datetime.strptime(combined_time, '%B %d, %Y %I %p') 

        #Regex to find a Eastern or Pacific Pattern
        timezone = re.findall(r'(\d*\d*:*\d*\d (PM|AM) (PT|PST|Pacific|Eastern))', b[0])[0][-1]

        #Eastern Timezone if timestamp is originally in Eastern Time and to convert to Pacific Time.
        if timezone == 'Eastern':
            convert_timezone = 'EST'
            try:
                convert_time = datetime.strptime(combined_time, '%B %d, %Y %I:%M %p') - timedelta(hours=3)
            except:
                convert_time = datetime.strptime(combined_time, '%B %d, %Y %I %p') - timedelta(hours=3)

        return convert_time
    except:
        convert_time = 0
        return convert_time


#mySQL query to pull distinct urls from table cashapp.
mycursor.execute("SELECT distinct url FROM cashapp")

myresult = mycursor.fetchall()

#Iterates the mySQL query output and appends to a list to compare against the scraped urls.
url_list = []

for item in myresult:
    url = item[0]
    url_list.append(url)

#Begin Function or Start of Script
sitemap(url_list)

#commit all changes to the mySQL database.
# conn.commit()
mydb.commit()


