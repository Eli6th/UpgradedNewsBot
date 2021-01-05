# UpgradedNewsBot
Before using pip install:

pip install requests

pip install beautiful soup 4

pip install smtplib

pip install redis

pip install nytimesarticle

pip install GoogleNews

pip install matplotlib

pip install tabulate

This upgraded bot will automatically send you an email from google news, NewYork Times, and/or newsYcombinator using the keywords inputted by the user. These inputs and sources can be added or removed in the importInfo.py script.

I would recommend turning off the New York Times email, unless you would like to sign up for their free developer account and get your own API key. To get the weather function working you would have to sign up for the open weather API and get your own API key.

At the moment it only works with the three news sources, the New York Times, Google News, and news y combinator. These easily can be expanded upon if you so choose, just add an if statement to the parse method/def and figure out how the api works for that news source. Would highly recommend adding other news sources if you want.

Keywords are unlimited and defined seperately, thus you can have a wide variety of topics to get your news from.

This project was done in part by Aaron Jack's tutorial, I expanded upon it by adding the New York Times and Google News. I also included the weather which will send with a formatted table and a graph showing the user the weather for the day. A link can be seen below to the exact tutorial: https://www.youtube.com/watch?v=1UMHhJEaVTQ
