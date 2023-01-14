import requests
import time as t
import xlsxwriter
import pandas
import argparse
import json
import random, os
import jaydebeapi
import argparse
import re
import threading
import asyncio
from requests_oauthlib import OAuth1, OAuth1Session
from datetime import *
from dateutil import parser
from auth import *
from filters import *
from pyfiglet import Figlet
###########################################################################################################################################################################
                  ####################################################### Classes #########################################################


############################# User #############################################
class PublicMetrics:
    followers_count: int
    following_count: int
    tweet_count: int
    listed_count: int

    def __init__(self, followers_count: int, following_count: int, tweet_count: int, listed_count: int) -> None:
        self.followers_count = followers_count
        self.following_count = following_count
        self.tweet_count = tweet_count
        self.listed_count = listed_count


class User:
	description: str
	verified: bool
	public_metrics: PublicMetrics
	location: str
	id: str
	name: str
	created_at: datetime
	username: str
	profile_image_url: str

	def __init__(self, description: str, verified: bool, public_metrics: PublicMetrics, id: str, name: str, created_at: datetime, username: str, profile_image_url: str) -> None:
		self.description = description
		self.verified = verified
		self.public_metrics = public_metrics
		self.id = id
		self.name = name
		self.created_at = created_at
		self.username = username
		self.profile_image_url = profile_image_url

############################# Tweet #############################################

class PublicMetricsTweet:
    retweet_count: int
    reply_count: int
    like_count: int
    quote_count: int

    def __init__(self, retweet_count: int, reply_count: int, like_count: int, quote_count: int) -> None:
        self.retweet_count = retweet_count
        self.reply_count = reply_count
        self.like_count = like_count
        self.quote_count = quote_count


class Tweet:
    id: str
    created_at: datetime
    author_id: str
    public_metrics: PublicMetricsTweet
    text: str

    def __init__(self, id: str, created_at: datetime, author_id: str, public_metrics: PublicMetrics, text: str) -> None:
        self.id = id
        self.created_at = created_at
        self.author_id = author_id
        self.public_metrics = public_metrics
        self.text = text



## Args parser
parser = argparse.ArgumentParser(description='Twiter Bot arguments commands')
parser.add_argument('--follow', type=str, help='fusrf - follow followers of an user, fhtg - follow by hastag, ')
parser.add_argument('--unfollow', type=str, help='myfollows - unfollow your follows')
parser.add_argument('--amount', type=int, help='enter amount to interact from 1 - 1000')
parser.add_argument('--username', type=str, help='username of the user you want to interact')
parser.add_argument('--hashtag', type=str, help='hashtag to interact with')
parser.add_argument('--scrape', type=str, help='myfollowers, userlikes, usertweets - to scrape your followers and save to database')
parser.add_argument('--unlike', type=str, help='tweets - unlike liked tweets by your account')
parser.add_argument('--like', type=str, help='usrtweet - like liked tweets by your account')

args = parser.parse_args()

## PyFigmet
f = Figlet(font='smkeyboard')
print(f.renderText('Twitter Bot'))
print(f.renderText('by MikeGrep'))


## Databse
path = os.path.abspath(os.getcwd())
conn = jaydebeapi.connect("org.h2.Driver","jdbc:h2:~/twitter-bot-databse",["sa", ""], path + "/h2-2.1.214.jar",)
curs = conn.cursor()
curs.execute('CREATE TABLE IF NOT EXISTS followed_users(id int primary key auto_increment, follow_username varchar(50), follow_id varchar(50), date_followed varchar(40))')
curs.execute('CREATE TABLE IF NOT EXISTS user_follows_next_token(id int primary key auto_increment, username varchar(50), next_token varchar(50))')
curs.execute('CREATE TABLE IF NOT EXISTS followed_history(id int primary key auto_increment, username varchar(50), follow_id varchar(50))')
curs.execute('CREATE TABLE IF NOT EXISTS my_followers(id int primary key auto_increment, username varchar(50), follow_id varchar(50))')
curs.execute('CREATE TABLE IF NOT EXISTS liked_tweets_next_token(id int primary key auto_increment, user_id varchar(50), next_token varchar(50))')
curs.execute('CREATE TABLE IF NOT EXISTS hashtag_next_token(id int primary key auto_increment, hashtag varchar(50), next_token varchar(50))')
curs.execute('CREATE TABLE IF NOT EXISTS user_tweets_next_token(id int primary key auto_increment, user_id varchar(50), next_token varchar(50))')


HEADERS = {'Content-Type': 'application/json', 'Accept': '*/*'}
BEARER_TOKEN = {'Authorization' : 'Bearer ' + BEARER_TOKEN}

OAUTH = OAuth1(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


def userMe():
	response = requests.get("https://api.twitter.com/2/users/me", auth=OAUTH)
	# print(response.json())


def followUser(accountId, userId):
    payload = {"target_user_id":str(userId)}
    response = requests.post("https://api.twitter.com/2/users/" + accountId + "/following", data=json.dumps(payload), headers=HEADERS, auth=OAUTH)
    try:
        if("Too Many Requests" in str(response.json()['title'])):
            t.sleep(906)
            print("Too Many Requests time sleep of 15 min")
            response = requests.post("https://api.twitter.com/2/users/" + accountId + "/following", data=json.dumps(payload), headers=HEADERS, auth=OAUTH)
    except:
        pass
    return response.status_code

def unfollowUser(accountId, userId):
    response = requests.delete("https://api.twitter.com/2/users/" + accountId + "/following/" + userId, auth=OAUTH)
    try:
        if("Too Many Requests" in str(response.json()['title'])):
            t.sleep(906)
            print("Too Many Requests time sleep of 15 min")
            response = requests.delete("https://api.twitter.com/2/users/" + accountId + "/following/" + userId, auth=OAUTH)
    except:
        pass
    return response.json()

def userRetweetsById(userId):
	response = requests.get("https://api.twitter.com/2/users/" + str(userId) + "/tweets?tweet.fields=author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld", auth=OAUTH)
	##print(response.json())

def getUserTweetsLikes(id, nextToken):
    response = None
    if(next_token != None):
        response = requests.get("https://api.twitter.com/2/users/" + str(id) + "/liked_tweets?max_results=75&pagination_token=" + nextToken + "&expansions=author_id&tweet.fields=created_at,author_id", headers=BEARER_TOKEN)
    else:
        response = requests.get("https://api.twitter.com/2/users/" + str(id) + "/liked_tweets?max_results=75&expansions=author_id&tweet.fields=created_at,author_id", headers=BEARER_TOKEN)
    try:
        if("Too Many Requests" in str(response.json()['title'])):
            t.sleep(906)
            print("Too Many Requests time sleep of 15 min")
            response = requests.delete("https://api.twitter.com/2/users/" + accountId + "/following/" + userId, auth=OAUTH)
    except:
        pass

    return response.json()


def getMyFollowersToDatabse():
        curs.execute("DELETE FROM my_followers")
        amount = 0
        followersResultList = list()
        userId = getUserId(USERNAME)
        nextToken = None
        userFollowersAmount = getUserInfoById(userId).public_metrics.followers_count
        while(amount < userFollowersAmount):
            try:
                curs.execute("SELECT * FROM user_follows_next_token WHERE username = '" + str(USERNAME) + "'")
                nextToken = curs.fetchone()
                nextToken = nextToken[2]
                print(nextToken + " fetch")

            except:
                pass

            users = getUserFollowers(userId, 1000, nextToken, USERNAME)
            followersResultList.extend(users)
            amount = len(followersResultList)
            sleep = random.randrange(60, 68)
            t.sleep(sleep)

            for user in users:
                curs.execute("INSERT INTO my_followers (username, follow_id) VALUES ('" + user.username + "', '" + user.id + "')")
            conn.commit()

        curs.execute("DELETE FROM user_follows_next_token WHERE username = '" + USERNAME + "'")




        print("All Followers are in database.Can start to unfollow them")

def getUsersTweetes(userId, nextToken, amount):
    tweetsResultList = list()

    if(nextToken != None):
    	response = requests.get("https://api.twitter.com/2/users/" + userId + "/tweets?max_results=" + str(amount) + "&pagination_token=" + str(nextToken) +
    		"&tweet.fields=id,created_at,public_metrics,text,author_id", headers=BEARER_TOKEN)
    else:
    	response =requests.get("https://api.twitter.com/2/users/" + userId + "/tweets?max_results=" + str(amount) + "&tweet.fields=id,created_at,public_metrics,text,author_id",
    	 headers=BEARER_TOKEN)
    # print(response.json())
    tweetList = response.json()['data']
    try:
        nextToken =  response.json()['meta']['next_token']
        curs.execute("DELETE FROM user_tweets_next_token WHERE username = '" + str(userId) + "'")
        curs.execute("INSERT INTO user_tweets_next_token (username, next_token) VALUES ('" + str(userId) + "', '" + str(nextToken) + "')")
    except:
        pass

    for tweet in tweetList:
    	tweetResult = Tweet(tweet['id'], tweet['created_at'], tweet['author_id'], PublicMetricsTweet(tweet['public_metrics']['retweet_count'], tweet['public_metrics']['reply_count'], tweet['public_metrics']['like_count'], tweet['public_metrics']['quote_count']), tweet['text'])
    	tweetsResultList.append(tweetResult)

    return tweetsResultList


def getTweetsByHashtag(hashtag, amount, nextToken):
    searchAmount = 0
    tweetList = list()
    tweetsResultList = list()
    if(amount > 100):
        while(amount > 0):
            if(amount > 100):
                searchAmount = 100
            else:
                searchAmount = amount

            if(nextToken != None):
                nextToken = "&next_token=" + nextToken
            else:
                nextToken = ""

            response = requests.get("https://api.twitter.com/2/tweets/search/recent?query=" + hashtag + "&max_results=" + str(searchAmount) + nextToken + "&tweet.fields=author_id,created_at,id,possibly_sensitive,text,withheld", headers=BEARER_TOKEN)
            # print(response.json())
            amount -= len(response.json()['data'])
            try:
                nextToken = response.json()['meta']['next_token']
                curs.execute("INSERT INTO hashtag_next_token (hashtag, next_token) VALUES ('" + str(hashtag) + "', '" + str(nextToken) + "')")

            except:
                pass

            try:
                tweetList = response.json()['data']
                for tweet in tweetList:
                    tweetResult = Tweet(tweet['id'], tweet['created_at'], tweet['author_id'], None, tweet['text'])
                    tweetsResultList.append(tweetResult)
            except:
                break



    else:
        response = requests.get("https://api.twitter.com/2/tweets/search/recent?query=" + hashtag + "&max_results=" + str(amount) + "&tweet.fields=author_id,created_at,id,possibly_sensitive,text,withheld", headers=BEARER_TOKEN)
        print(response.json())
        try:
            tweetList = response.json()['data']
        except:
            pass

    for tweet in tweetList:
        tweetResult = Tweet(tweet['id'], tweet['created_at'], tweet['author_id'], None, tweet['text'])
        tweetsResultList.append(tweetResult)

    return tweetsResultList



def getUserId(username):
	response = requests.get("https://api.twitter.com/2/users/by/username/" + username + "?tweet.fields=id", headers=BEARER_TOKEN)

	return response.json()['data']['id']

def getUserById(userId):
    response = requests.get("https://api.twitter.com/2/users/" + str(userId) + "?user.fields=created_at,location,name,username", headers=BEARER_TOKEN)

    return response.json()['data']

def getUserInfoById(id):
    response = requests.get("https://api.twitter.com/2/users/" + id + "?user.fields=created_at,description,id,location,name,profile_image_url,public_metrics,username,verified", headers=BEARER_TOKEN)
    user = response.json()['data']

    return User(user['description'], user['verified'], PublicMetrics(user['public_metrics']['followers_count'], user['public_metrics']['following_count'], user['public_metrics']['tweet_count'], user['public_metrics']['listed_count']), user['id'], user['name'], user['created_at'], user['username'], user['profile_image_url'])

def likeTweet(userId, tweetId):
    payload = '{"tweet_id":' + str(tweetId) + '}'
    response = requests.post("https://api.twitter.com/2/users/" + str(userId) + "/likes", headers=HEADERS, data=json.dumps(payload), auth=OAUTH)
    try:
        if("Too Many Requests" in str(response.json()['title'])):
            t.sleep(906)
            print("Too Many Requests time sleep of 15 min")
            response = requests.post("https://api.twitter.com/2/users/" + str(userId) + "/likes", headers=HEADERS, data=json.dumps(payload), auth=OAUTH)
    except:
        pass

    return response.status_code


def getUserFollowers(userId, amount, paginationToken, username):
    pagintation = ""
    usersListResult = list()
    if(paginationToken != None):
    	pagintation = "&pagination_token=" + str(paginationToken)

    response = requests.get("https://api.twitter.com/2/users/" + str(userId) + "/followers?max_results=" + str(amount) + pagintation +"&user.fields=created_at,description,id,location,name,profile_image_url,public_metrics,username,verified&tweet.fields=public_metrics,text", headers=BEARER_TOKEN)
    print(response)
    usersList = response.json()['data']
    try:
        nextToken = response.json()['meta']['next_token']
        print(nextToken)
        if(len(nextToken) > 3):
            curs.execute("MERGE INTO user_follows_next_token (username, next_token) KEY (username) VALUES ('" + str(username) + "', '" + str(nextToken) + "')")
    except:
        pass

    for user in usersList:
    	userResult =  User(user['description'], user['verified'], PublicMetrics(user['public_metrics']['followers_count'], user['public_metrics']['following_count'], user['public_metrics']['tweet_count'], user['public_metrics']['listed_count']), user['id'], user['name'], user['created_at'], user['username'], user['profile_image_url'])
    	usersListResult.append(userResult)

    return usersListResult;

def getUserFollowing(userId, amount):
    pagintation = ""
    usersListResult = list()

    response = requests.get("https://api.twitter.com/2/users/" + userId + "/following?max_results=" + str(amount) + "&user.fields=description,id,location,name,profile_image_url,protected,public_metrics,username,verified", auth=OAUTH)
    print(response)
    userList = response.json()['data']

    for user in userList:
        userResult =  User(user['description'], user['verified'], PublicMetrics(user['public_metrics']['followers_count'], user['public_metrics']['following_count'], user['public_metrics']['tweet_count'], user['public_metrics']['listed_count']), user['id'], user['name'], None, user['username'], user['profile_image_url'])
        usersListResult.append(userResult)

    return usersListResult


def blockUser(accountId, userId):
    payload = {"target_user_id":str(userId)}
    response = requests.post("https://api.twitter.com/2/users/" + str(accountId) + "/blocking", data=json.dumps(payload), headers=HEADERS, auth=OAUTH )
    print(response)


def unlikeTweet(tweetId, userId):
    response = requests.delete("https://api.twitter.com/2/users/" + str(userId) + "/likes/" + str(tweetId), auth=OAUTH)
    print(response)

def getUserLikedTweets(userId, amount):
    nextToken = ""
    currentAmount = 0
    tweetListResult = list()

    while(amount > 0):
        if(amount > 100):
            currentAmount = 100
        else:
            currentAmount = amount
        try:
            curs.execute("SELECT * FROM liked_tweets_next_token WHERE user_id = " + userId)
            data = curs.fetchone()
            nextToken = "&pagination_token=" + data[2]
        except:
            pass

        response = requests.get("https://api.twitter.com/2/users/" + userId + "/liked_tweets?max_results=" + str(currentAmount)  + nextToken + "&tweet.fields=author_id,created_at,id,public_metrics,text", headers=BEARER_TOKEN)
        print(response)
        tweetsList = response.json()['data']
        amount -= currentAmount

        try:
            nextToken = "&pagination_token=" + response.json()['meta']['next_token']
            curs.execute("DELETE FROM liked_tweets_next_token WHERE user_id = " + userId)
            curs.execute("INSERT INTO liked_tweets_next_token (user_id, next_token) VALUES ('" + str(userId)  + "', '" + str(nextToken) + "')")
        except:
            nextToken = ""

        for tweet in tweetsList:
            tweetResult = Tweet(tweet['id'], tweet['created_at'], tweet['author_id'], PublicMetricsTweet(tweet['public_metrics']['retweet_count'], tweet['public_metrics']['reply_count'], tweet['public_metrics']['like_count'], tweet['public_metrics']['quote_count']), tweet['text'])
            tweetListResult.append(tweetResult)

        t.sleep(random.randrange(58, 68))

    return tweetListResult

def exportUserTweetLikes(username, amount):
    myLikesWorkBook = xlsxwriter.Workbook(username + ' likes-' + str(datetime.timestamp(datetime.now())) + '.xlsx')
    myLikesSheet = myLikesWorkBook.add_worksheet()

    row = 0
    col = 0

    myLikesSheet.write(row, col, "Tweet ID")
    myLikesSheet.write(row, col + 1, "Author Id ")
    myLikesSheet.write(row, col + 2, "Author Username")
    myLikesSheet.write(row, col + 3, "Author Name")
    myLikesSheet.write(row, col + 4, "Author Created At")
    myLikesSheet.write(row, col + 5, "Created At")
    myLikesSheet.write(row, col + 6, "Text")
    myLikesSheet.write(row, col + 7, "Retweet Count")
    myLikesSheet.write(row, col + 8, "Replay Count")
    myLikesSheet.write(row, col + 9, "Likes Count")

    row += 1
    userId = getUserId(username)
    likedTweetsList = getUserLikedTweets(userId, amount)
    for tweet in likedTweetsList:
        userResponse = getUserById(tweet.author_id)
        myLikesSheet.write(row, col, tweet.id)
        myLikesSheet.write(row, col + 1, tweet.author_id)
        myLikesSheet.write(row, col + 2, userResponse['username'])
        myLikesSheet.write(row, col + 3, userResponse['name'])
        myLikesSheet.write(row, col + 4, userResponse['created_at'])
        myLikesSheet.write(row, col + 5, tweet.created_at)
        myLikesSheet.write(row, col + 6, tweet.text)
        myLikesSheet.write(row, col + 7, tweet.public_metrics.retweet_count)
        myLikesSheet.write(row, col + 8, tweet.public_metrics.reply_count)
        myLikesSheet.write(row, col + 9, tweet.public_metrics.like_count)
        row += 1
        t.sleep(random.randrange(60, 75))

    myLikesWorkBook.close()


def exportUsersTweets(username, amount):
    userId = getUserId(username)
    userTweetList = list()
    myLikesWorkBook = xlsxwriter.Workbook(username + '- Tweets -' + str(datetime.timestamp(datetime.now())) + '.xlsx')
    myLikesSheet = myLikesWorkBook.add_worksheet()

    row = 0
    col = 0

    myLikesSheet.write(row, col, "Tweet ID")
    myLikesSheet.write(row, col + 1, "Author Id ")
    myLikesSheet.write(row, col + 2, "Created At")
    myLikesSheet.write(row, col + 3, "Text")
    myLikesSheet.write(row, col + 4, "Retweet Count")
    myLikesSheet.write(row, col + 5, "Reply Count")
    myLikesSheet.write(row, col + 6, "Like Count")
    myLikesSheet.write(row, col + 7, "Quote Count")

    row += 1

    while amount > 0:
        try:
            curs.execute("SELECT * FROM user_tweets_next_token WHERE user_id = '" + str(userId) + "'")
            data = curs.fetchone()
            nextToken = data[2]
        except:
            nextToken = None

        userTweetList = getUsersTweetes(userId, nextToken, amount)

        amount -= len(userTweetList)

        for tweet in userTweetList:
        	myLikesSheet.write(row, col, tweet.id)
        	myLikesSheet.write(row, col + 1, tweet.author_id)
        	myLikesSheet.write(row, col + 2, tweet.created_at)
        	myLikesSheet.write(row, col + 3, tweet.text)
        	myLikesSheet.write(row, col + 4, tweet.public_metrics.retweet_count)
        	myLikesSheet.write(row, col + 5, tweet.public_metrics.reply_count)
        	myLikesSheet.write(row, col + 6, tweet.public_metrics.like_count)
        	myLikesSheet.write(row, col + 6, tweet.public_metrics.quote_count)

        	row += 1

    myLikesWorkBook.close()
    curs.execute("DELETE FROM user_tweets_next_token WHERE user_id = '" + str(userId) + "'")



def getBlockedAccounts():
    blockedAccountList = list()
    workbook = pandas.read_excel("blocked.xlsx")
    df = workbook['Col1']

    for i in range(len(df.index)):
        blockedAccountList.append(str(df[i]).replace("@", ""))

    return blockedAccountList

def filtersCount():
	count = 0
	if(BIO_KEYWORD):
		count += 1
	if(FOLLOWERS):
		count += 1
	if(FOLLOWING):
		count += 1
	if(TWEETS):
		count += 1
	if(PROFILE_IMAGE):
		count += 1
	if(TALKATIVE):
		count += 1

	return count

def isCyrilic(text):
    return bool(re.search('[\u0400-\u04FF]', text))

def isRepeatedWords(text):
    isRepeat = False
    words = text.lower().split(" ")
    for i in range(0, len(words)):
       count = 1
       for x in range(i+1, len(words)):
          if(words[i] == (words[x])):
             count = count + 1
             # To prevent printing a visited word,
             # set words[x] to 0
             words[x] = "0"
       # duplicate word if count is more than 1
       if(count > 2 and words[i] != "0"):
          isRepeat = True

    return isRepeat

def getFollowersFromDataBase():
    myFollowers = list()
    curs.execute('SELECT * FROM my_followers')
    users = curs.fetchall()
    for user in users:
        myFollowers.append(user[1])

    return myFollowers

def followFollowersOfAnUser(username, amount, recursion, isThread):
    historyFollows = getFollowingHistorty()
    userId = getUserId(username)
    accountId = getUserId(USERNAME)
    blockedList = getBlockedAccounts()
    nextToken = ""
    t1 = 40
    t2 = 65
    if isThread:
        t1 = 80
        t2 = 120

    try:
        curs.execute("SELECT * FROM user_follows_next_token WHERE username = '" + str(username) + "'")
        nextToken = curs.fetchone()
        nextToken = nextToken[2]
        print(nextToken + " fetch")
    except:
        pass

    users = getUserFollowers(userId, amount, nextToken, username)

    filteredUsers = filterUsers(users)

    for user in filteredUsers:
        if(user.username in historyFollows):
            filteredUsers.remove(user)
            print(user.username + "  is already interacted user skiping!")

    ## Blocked account ignore
    for user in filteredUsers:
        if user.username in blockedList:
            filteredUsers.remove(user)
        if isCyrilic(user.description):
            try:
                filteredUsers.remove(user)
            except:
                pass
        if isRepeatedWords(user.description):
            try:
                filteredUsers.remove(user)
            except:
                pass


    items = list(range(0, len(filteredUsers)))
    print("In follow by usr follwers")
    for user,items in zip(filteredUsers, progressBar(items, prefix = 'Progress:', suffix = 'Complete', length = 50)):
        if(followUser(accountId, user.id) == 200):
            print(user.username + " followed")
            t.sleep(random.randrange(t1, t2))
            curs.execute("INSERT INTO followed_users (follow_username, follow_id, date_followed) VALUES ('" + str(user.username)  + "', '" + str(user.id) + "', '" + datetime.today().strftime("%Y-%m-%dT%H:%M:%S.%fZ") + "')")
            curs.execute("INSERT INTO followed_history (username, follow_id) VALUES ('" + str(user.username)  + "', '" + str(user.id) + "')")


    user = getUserInfoById(userId)
    if len(filteredUsers) < amount and user.public_metrics.followers_count >= amount:
        amount -= len(filteredUsers)
        if amount < 10:
            return
        followFollowersOfAnUser(username, amount, True, isThread)


def followByHashtag(hashtag, amount, recursion, isThread):
    nextToken = None
    t1 = 30
    t2 = 65
    if isThread:
        t1 = 60
        t2 = 180
    if(recursion == True):
        try:
            curs.execute("SELECT * hashtag_next_token WHERE hashtag = '" + str(hashtag) + "'")
            data = curs.fetchone()
            nextToken = data[2]
        except:
            pass

    resultTweets = getTweetsByHashtag(hashtag, amount, nextToken)
    historyFollows = getFollowingHistorty()
    accountId = getUserId(USERNAME)
    blockedList = getBlockedAccounts()
    usersSet = set()

    for tweet in resultTweets:
        isBlackList = False
        for word in BLACK_LIST:
            if(word in tweet.text):
                print("Found black list word '" + word + "' skiping tweet!")
                isBlackList = True
                break
        try:
            if not isBlackList:
                user = getUserInfoById(tweet.author_id)
                usersSet.add(user)
        except:
            pass

    filteredUsers = filterUsers(usersSet)

    for user in filteredUsers:
        if(user.username in historyFollows):
            filteredUsers.remove(user)
            print(user.username + "  is already interacted user skiping!")

    ## Blocked account ignore
    for user in filteredUsers:
        if user.username in blockedList:
            filteredUsers.remove(user)
        if isCyrilic(user.description):
            try:
                filteredUsers.remove(user)
            except:
                pass
        if isRepeatedWords(user.description):
            try:
                filteredUsers.remove(user)
            except:
                pass

    print("In follow by hashtag")
    items = list(range(0, len(filteredUsers)))
    for user,item in zip(filteredUsers,progressBar(items, prefix = 'Progress:', suffix = 'Complete', length = 50)):
        if(followUser(accountId, user.id) == 200):
            print(user.username + " followed")
            t.sleep(random.randrange(t1, t2))
            curs.execute("INSERT INTO followed_users (follow_username, follow_id, date_followed) VALUES ('" + str(user.username)  + "', '" + str(user.id) + "', '" + datetime.today().strftime("%Y-%m-%dT%H:%M:%S.%fZ") + "')")


    if len(filteredUsers) < amount:
        amount -= len(filteredUsers)
        if amount < 10:
            return
        followByHashtag(hashtag, amount, True, isThread)


def unfollowMyFollowings(amount):
    myUserId = getUserId(USERNAME)
    user = getUserInfoById(myUserId)
    usersList = ing(myUserId, amount)

    filteredUsers = filterUsers(usersList)
    filteredUsers = usersList
    if(DO_NOT_FOLLOW_BACK):
        userMyFollowers = getFollowersFromDataBase()
        for userForUnfollow in filteredUsers:
            if(userForUnfollow.username in userMyFollowers):
                filteredUsers.remove(userForUnfollow)

    items = list(range(0, len(filteredUsers)))
    for user,items in zip(filteredUsers, progressBar(items, prefix = 'Progress:', suffix = 'Complete', length = 50)):
        response = unfollowUser(myUserId, user.id)
        print(response)
        print("Successfuly unfollowed user: " + user.username)
        curs.execute("DELETE FROM followed_users WHERE follow_id = '" + str(userIdUnfollow) + "'")
        t.sleep(random.randrange(30, 65))

def databseFollowings():
    minimumDate = datetime.today() - timedelta(days=DAYS_FOR_UNFOLLOWING)
    format_data = "%Y-%m-%dT%H:%M:%S.%fZ"
    followingIds = list()

    curs.execute("SELECT * FROM followed_users")
    followingResult = curs.fetchall()
    for follow in followingResult:
        if(datetime.strptime(follow[3], format_data) <= minimumDate):
            followingIds.append(follow[2])

    return followingIds

def likeUsersTweets(tweetsList, isThread):
    userId = getUserId(USERNAME)
    t1 = 60
    t2 = 80
    if isThread:
        t1 = 120
        t2 = 190
    print("in like user tweets")
    for tweet in tweetsList:
        response = likeTweet(userId, tweet.id)
        if response == 200:
            print("Tweet with id: " + tweet.id  + " liked")
            t.sleep(t1, t2)


def unlikeLikedTweets(amount):
    userId = getUserId(USERNAME)
    nextToken = None

    likedTweets = getUserLikedTweets(userId, amount)

    items = list(range(0, len(likedTweets)))
    for likedTweet, items in zip(likedTweets, progressBar(items, prefix = 'Progress:', suffix = 'Complete', length = 50)):
        unlikeTweet(likedTweet.id, userId)
        print("Tweet with id: " + likedTweet.id + " unliked Successfuly")
        t.sleep(random.randrange(40, 65))

def getUserMeFollowers():
    amount = 1000
    followersResultList = list()
    userId = getUserId(USERNAME)
    nextToken = None
    userFollowersAmount = getUserInfoById(userId).public_metrics.followers_count
    while(amount < userFollowersAmount):
        try:
            curs.execute("SELECT * FROM user_follows_next_token WHERE username = '" + str(username) + "'")
            nextToken = curs.fetchone()
            nextToken = nextToken[2]
            print(nextToken + " fetch")
        except:
            pass

        users = getUserFollowers(userId, amount, nextToken, USERNAME)
        followersResultList.extend(users)
        amount = len(users)
        sleep = random.randrange(30, 65)
        t.sleep(sleep)

        for user in followersResultList:
            if(user in WHITE_LIST):
                followersResultList.remove(user)

    return followersResultList

def filterUsers(userList):
    userListResult = list()
    usersList = list()
    countFilter = filtersCount()
    count = 0

    for user in userList:
        isBlackList = False
        if(BIO_KEYWORD):
        	if(BIO_KEYWORD_STRING in user.description):
        		count += 1
        if(FOLLOWERS):
        	if(user.public_metrics.followers_count >= FOLLOWERS_COUNT_FROM and user.public_metrics.followers_count <= FOLLOWERS_COUNT_TO):
        		count += 1
        if(FOLLOWING):
        	if(user.public_metrics.following_count >= FOLLOWING_COUNT_FROM and user.public_metrics.following_count <= FOLLOWING_COUNT_TO):
        		count += 1
        if(TWEETS):
        	if(user.public_metrics.tweet_count >= TWEET_COUNT_FROM and user.public_metrics.tweet_count <= TWEET_COUNT_TO):
        		count += 1
        if(PROFILE_IMAGE):
        	if(len(user.profile_image_url) > 0):
        		count += 1
        if(TALKATIVE):
        	if(isTalkative(user.username)):
                    count += 1
        if(count == countFilter):
            if(VERIFIED != user.verified):
                continue
            for blackListWord in BLACK_LIST:
                if(blackListWord in user.description):
                    isBlackList = True
                    break
            if not isBlackList:
                userListResult.append(user)
        else:
            print(user.username + " does not match the filters skip user!")
        count = 0

    return userListResult

def isTalkative(username):
    minimumDate = datetime.today() - timedelta(days=10)
    format_data = "%Y-%m-%dT%H:%M:%S.%fZ"
    isTalkative = False
    userId = getUserId(username)
    try:
        tweetsList = getUsersTweetes(userId, None, 10)
        for tweet in tweetsList:
            if(datetime.strptime(tweet.created_at, format_data) >= minimumDate):
                isTalkative = True
                break;
    except:
       pass

    return isTalkative

def getFollowingHistorty():
    historyList = list()
    try:
        curs.execute("SELECT * FROM followed_history")
        data = curs.fetchall()
        for record in data:
            historyList.append(record[1])
    except:
        pass

    return historyList


def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        print()
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()



########################################################################################
################################## Multy Actions #################################
isMultiThred = False
threadList = list()
numActions = int()
numActions = 0

if args.follow != None:
    numActions += len(args.follow.split(" "))

if args.like != None:
    numActions += 1

if args.unlike != None:
    numActions += 1


if args.follow != None and "fusrf" in args.follow and len(args.follow) > 3:
    treadFollowers = threading.Thread(target=followFollowersOfAnUser, args=(str(args.username),round(int(args.amount) / numActions), False, True))
    threadList.append(treadFollowers)
    t.sleep(60)
    print("Follow by User followers start")


if args.follow != None and "fhtg" in args.follow and len(args.follow) > 3:
    treadHashtag = threading.Thread(target=followByHashtag, args=(str(args.hashtag),round(int(args.amount) / numActions), False, True))
    threadList.append(treadHashtag)
    print("Follow by hashtag start")

if args.like != None and "usrtweets" in args.like and len(args.like) > 7:
    userId = getUserId(str(args.username))
    nextToken = None

    try:
        curs.execute("SELECT * FROM user_tweets_next_token WHERE user_id = '" + str(userId) + "'")
        data = curs.fetchone()
        nextToken = data[2]
    except:
        pass

    tweetList = getUsersTweetes(str(userId), nextToken, 20)
    threadLikeTweets = threading.Thread(target=likeUsersTweets, args=(tweetList, True))
    threadList.append(threadLikeTweets)
    print("Like user tweets with amount 20 start")

if args.unlike != None and "tweets" in args.unlike and isMultiThred == True:
    threadUnlikeTweets = threading.Thread(target=unlikeLikedTweets, args=(round(int(args.amount) / numActions)))
    print("Unlike my likes started")
    threadList.append(threadUnlikeTweets)


if len(threadList) > 1:
    isMultiThred = True

amount = args.amount

if isMultiThred:
    index = 0
    while(amount > 0):
        currentThread  = threadList[index]
        currentThread.start()
        while currentThread.is_alive():
            t.sleep(1)

        index += 1
        amount -= (amount / numActions)
        if index == len(threadList):
            break


########################################## SINGLE ACTIONS ####################################################
##############################################################################################################
if not isMultiThred:
    if args.follow == "fusrf":
        followFollowersOfAnUser(str(args.username), int(args.amount), False, False)
        print("Bot finished with following actions.You can run again.")
    if args.follow == "fhtg":
        followByHashtag(str(args.hashtag), int(args.amount), False, False)
        print("Bot finished with following actions.You can run again.")
    if args.unfollow == "myfollows":
        unfollowMyFollowings(int(args.amount))
        print("Bot finished with unfollowing actions.You can run again.")
    if args.scrape == "myfollowers":
        getMyFollowersToDatabse()
        print("Bot finished with scrapping followers")
    if args.scrape == "userlikes":
        exportUserTweetLikes(str(args.username), int(args.amount))
        print("Bot finish with scraping user: " + args.username + " likes. You can run again.")
    if args.scrape == "usertweets":
        exportUsersTweets(str(args.username), int(args.amount))
        print("Bot finish with scraping tweets of user: "  + args.username + " You can run again.")
    if args.unlike == "tweets":
        unlikeLikedTweets(int(args.amount), e)
        print("Bot finish with unliking tweets. You can run again")
    if args.like == "usrtweets":
        userId = getUserId(str(args.username))
        nextToken = None

        try:
            curs.execute("SELECT * FROM user_tweets_next_token WHERE user_id = '" + str(userId) + "'")
            data = curs.fetchone()
            nextToken = data[2]
        except:
            pass

        tweetList = getUsersTweetes(str(userId), nextToken, int(args.amount))
        likeUsersTweets(tweetList, False)
        print("Like user tweets finished")
