import requests #
import time #   
from bs4 import BeautifulSoup #
import datetime #
from nytimesarticle import articleAPI #
from GoogleNews import GoogleNews #
import csv
import smtplib #
import matplotlib.pyplot as plt #
import matplotlib.dates as mdates #
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from tabulate import tabulate
#this is to keep all the private information, should either edit script to create your own or create your own important info script
import importInfo

class Conversions:
    def convertTemp(self, temp):
        convertedTemp = int((temp - 273.15) * 9/5 + 32)
        return (convertedTemp)

    def convertTimeHour(self, enteredtime):
        if (int(time.strftime('%H',  time.gmtime(enteredtime))) - 4 < 0):
            convertedTime = int(time.strftime('%H',  time.gmtime(enteredtime))) + 20
        else:
            convertedTime = int(time.strftime('%H',  time.gmtime(enteredtime))) - 4
        return(convertedTime)

    def convertTimeDate(self, enteredtime):
        convertedTime = time.strftime('%m/%d/%Y',  time.gmtime(enteredtime))
        return(convertedTime)

class NewsWebScraper:

    #defining initial self terms
    def __init__(self, keywords, newsSources, weatherSources):
        self.hasArticles = False
        self.news_sources = newsSources
        self.markup = []
        self.read_links = [] 
        self.keywords = keywords
        self.cfg = Conversions()
        self.weather_sources = weatherSources
        self.openweather_api_key = importInfo.openweatherAPIKEY
        self.openweather_hourly = [[] for i in range(24)]
        self.current_time = []
        self.current_weather = []

    def weather_parse(self, lat, lon):
        #for the number of news sources you have loop through them
        for i in range(len(self.weather_sources)):
            if self.weather_sources[i] == 'OpenWeather':
                #requesting the api and extracting the json file from it
                r = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat=' + lat + '&lon=' + lon + '&%20exclude=hourly,daily&appid=' + self.openweather_api_key)
                json_object = r.json()
                
                #getting the current time and date
                current_time_e = json_object['current']['dt']
                self.current_time.append(self.cfg.convertTimeHour(current_time_e))
                self.current_time.append(self.cfg.convertTimeDate(current_time_e))

                #finding the date of tomorrow
                tomorrow = datetime.datetime.now() + datetime.timedelta(days = 1)

                #setting up hourly variables
                hourly_time = []
                hourly_showtime = []
                hourly_temp = []
                hourly_feels_like = []
                hourly_weather_description = []

                #assigning values of the hourly variables from the json file
                for i in range(24):
                    hourly_showtime.append(self.cfg.convertTimeHour(json_object['hourly'][i]['dt']))
                    hourly_temp.append(self.cfg.convertTemp(json_object['hourly'][i]['temp']))
                    hourly_feels_like.append(self.cfg.convertTemp(json_object['hourly'][i]['feels_like']))
                    hourly_weather_description.append(json_object['hourly'][i]['weather'][0]['description'])

                    self.openweather_hourly[i].append(self.cfg.convertTimeHour(json_object['hourly'][i]['dt']))
                    self.openweather_hourly[i].append(self.cfg.convertTemp(json_object['hourly'][i]['temp']))
                    self.openweather_hourly[i].append(self.cfg.convertTemp(json_object['hourly'][i]['feels_like']))
                    self.openweather_hourly[i].append(json_object['hourly'][i]['weather'][0]['description'])
                
                #creating the graph
                hourly_time = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(24)]
                plt.plot(hourly_time, hourly_temp) 
                plt.ylim(min(hourly_temp)-1, max(hourly_temp)+5)
                plt.gcf().autofmt_xdate()
                myFmt = mdates.DateFormatter('%H:%M')
                plt.gca().xaxis.set_major_formatter(myFmt)
                for i in range(24):
                    if (i % 2 == 0):
                        plt.annotate(str(hourly_showtime[i]) + ':00\n' + str(hourly_temp[i]) + '°F',(hourly_time[i], hourly_temp[i]), ha='center', va='baseline', xytext=(hourly_time[i], hourly_temp[i] + 1.5))
                #labeling the axes and title of the graph
                plt.xlabel("Time")
                plt.ylabel("Temperature (Degrees Farenheit)")
                plt.title('Daily Weather (Temp)\n' + str(time.strftime('%m/%d/%Y', datetime.datetime.now().timetuple())) + ' - ' + str(time.strftime('%m/%d/%Y', tomorrow.timetuple())))
                #saving the graph as a png file
                plt.figure(1).savefig("OpenWeather(Temperature).png")

    
    def parse(self):
        #for the number of news sources you have loop through them
        for i in range(len(self.news_sources)):
            if self.news_sources[i] == 'NewsYCombinator':
                #access the website and find all the stories on the front page
                self.markup.append(requests.get('https://news.ycombinator.com/').text)
                soup = BeautifulSoup(self.markup[i], 'html.parser')
                links = soup.findAll("a", {"class": "storylink"})
                self.saved_links = []
                #search all stories on front page to find out whether or not your key words are there
                for link in links:
                    for keyword in self.keywords:
                        if keyword in link.text:
                            self.saved_links.append(link)

                #get all of the links and save them, then declare that articles have been found
                for a in range(len(self.saved_links)):
                    self.read_links.append(str(self.saved_links[a]['href']))
                    self.hasArticles = True
            elif self.news_sources[i] == 'NewYorkTimes':
                #To get your api key go to nyt developers website create an account and create an app, then select search api and copy your key from there
                api = articleAPI(importInfo.newyorktimesArticleAPIKey)
                #loop through all key words to find out whether or not articles have them
                for a in range(len(self.keywords)):
                    if (datetime.datetime.now().day - 1 > 0):
                        articles = api.search( q = self.keywords[a], begin_date = datetime.datetime.now().year * 10000 + (datetime.datetime.now().month) * 100 + (datetime.datetime.now().day - 1), page=1 )
                    elif (datetime.datetime.now().month - 1 == 4 or datetime.datetime.now().month - 1 == 6 or datetime.datetime.now().month - 1 == 9 or datetime.datetime.now().month - 1 == 11):
                        articles = api.search( q = self.keywords[a], begin_date = datetime.datetime.now().year * 10000 + (datetime.datetime.now().month-1) * 100 + (datetime.datetime.now().day + 29), page=1 )
                    elif (datetime.datetime.now().month - 1 == 2 and datetime.datetime.now().year % 4 == 0):
                        articles = api.search( q = self.keywords[a], begin_date = datetime.datetime.now().year * 10000 + (datetime.datetime.now().month-1) * 100 + (datetime.datetime.now().day + 28), page=1 )
                    elif (datetime.datetime.now().month - 1 == 2):
                        articles = api.search( q = self.keywords[a], begin_date = datetime.datetime.now().year * 10000 + (datetime.datetime.now().month-1) * 100 + (datetime.datetime.now().day + 28), page=1 )
                    else:
                        articles = api.search( q = self.keywords[a], begin_date = datetime.datetime.now().year * 10000 + (datetime.datetime.now().month-1) * 100 + (datetime.datetime.now().day + 30), page=1 )
                    self.list_of_articles = []
                    for docs in articles['response']['docs']:
                        article_blurbs = {}
                        article_blurbs = docs.get('headline').get('main') + '\n' + docs.get('web_url') + '\n' + docs.get('snippet')
                        self.list_of_articles.append(str(article_blurbs))
                #if has an article, declare articles have been found
                if len(self.list_of_articles) > 0:
                    self.hasArticles = True
            elif self.news_sources[i] == 'GoogleNews':
                googlenews = GoogleNews()
                googlenews = GoogleNews(lang='en')
                googlenews = GoogleNews(start=str(datetime.datetime.now().month) + '/'+ str(datetime.datetime.now().day - 1) + '/'+ str(datetime.datetime.now().year),end=str(datetime.datetime.now().month) + '/'+ str(datetime.datetime.now().day) + '/'+ str(datetime.datetime.now().year))

                self.googleArticles = [[] for z in range(len(self.keywords))]
                for a in range(len(self.keywords)):
                    googlenews.search(self.keywords[a])
                    gnews = googlenews.result()
                    for docs2 in gnews:
                        self.googleArticles[a].append(str(docs2.get('title')) + '\n' + str(docs2.get('date')) + '\n' + str(docs2.get('link')) + '\n' + str(docs2.get('desc')))
                    googlenews.clear()
                
                if len(self.googleArticles) > 0:
                    self.hasArticles = True

    def email(self, addressNum):
        #setting up the email itself: where from, where to, and the subject
        from_address = importInfo.gmail_from_address
        to_address = email_addresses[addressNum]
        msg = MIMEMultipart()
        msg['From'] = ', '.join(from_address)
        msg['To'] = to_address
        msg['Subject'] = 'Daily News and Weather'

        #weather
        for i in range(len(self.weather_sources)):
            #sending email from Open Weather
            if self.weather_sources[i] == 'OpenWeather':
                body = 'Your Daily Weather \nDate: ' + str(self.current_time[1] + '\n\n')
                results = [[] for i in range (24)]
                for i in range (24):
                    for a in range (4):
                        if (a == 0):
                            results[i].append(str(self.openweather_hourly[i][a]) + ':00')
                        elif (a == 1):
                            results[i].append(str(self.openweather_hourly[i][a]) + '°F')
                        elif (a == 3):
                            results[i].append(str(self.openweather_hourly[i][a]))

                #formatting weather information into a table
                body += tabulate(results, headers=["Time", "Temp", "Description"], tablefmt="pipe")
                msg.attach(MIMEText(body, 'plain'))

                #attaching image to email
                with open('OpenWeather(Temperature).png', 'rb') as fp:
                    img = MIMEImage(fp.read())
                msg.attach(img)
        
        #if newsycombinator is chosen as one of the news networks this is where all of its links are stored
        links = self.read_links
        if (self.hasArticles):
            for i in range(len(self.news_sources)):
                #sending email from newsycombinator
                if self.news_sources[i] == 'NewsYCombinator':
                    body = 'These are some news links that we found from NewsYCombinator that you might like on ' + str(self.keywords) + ':\n\n' + '\n\n'.join(links)
                    msg.attach(MIMEText(body, 'plain'))
                #sending email from nyt
                if self.news_sources[i] == 'NewYorkTimes':
                    body2 = '\n\n These are some news links that we found from The New York Times that you might like on ' + str(self.keywords) + ':\n\n' + str("\n\n".join(self.list_of_articles))                    
                    msg.attach(MIMEText(body2, 'plain'))
                #sending email from Google News
                if self.news_sources[i] == 'GoogleNews':
                    body3 = '\n\n Google News \nThese are some news links that we found from Google News that you might like on ' + str(self.keywords) + ':' 
                    for a in range(len(self.keywords)):
                        body3 += '\n\n' + '--------------------------------' + '\n' + str(self.keywords[a]) + '\n' + '--------------------------------' + '\n\n' + str("\n\n".join(self.googleArticles[a]))
                    msg.attach(MIMEText(body3, 'plain'))
        else:
            #if nothing is found on the subject/keywords on either news network this will be displayed
            body = 'Unfortunately there were no articles from ' + str(self.news_sources) + " discussing " + ', '.join(self.keywords)
            msg.attach(MIMEText(body, 'plain'))

        #Enter from email and password (also make sure to allow unauthorized third parties to acces the gmail so the script will work. So don't use an important email!)
        password = importInfo.gmail_from_address_password

        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(from_address, password)
        text = msg.as_string()
        mail.sendmail(from_address, to_address, text)
        mail.quit()

weather_sources = importInfo.weather_sources
place = importInfo.place
news_sources = importInfo.news_sources
news_keywords = importInfo.news_keywords
email_addresses = importInfo.email_addresses

for i in range(len(email_addresses)):
    n = NewsWebScraper(news_keywords[i], news_sources, weather_sources)
    n.weather_parse(place[i][0], place[i][1])
    n.parse()
    n.email(i)