import praw
from datetime import datetime, timedelta
from time import sleep
from config import *

def printLog( message ):
    print( datetime.now(), end = " " )
    print( message )

def hasSource( post ):
    printLog( "Looking for source in " + post.title + " created by " + str( post.author ) )
    for comment in post.comments:
        if comment.author == post.author and "source:" in comment.body.lower():
            return True
    return False

def main():
    printLog( "Logging in..." )
    reddit = praw.Reddit( client_id = bot_id, client_secret = bot_secret, password = bot_pwd, user_agent = bot_agent, username = bot_usr )
    printLog( "Logged in..." )

    while True:
        printLog( "Looking at posts in " + bot_subreddit + "..." )
        for post in reddit.subreddit( bot_subreddit ).new():
            if datetime.now() - datetime.fromtimestamp( post.created_utc ) >= timedelta( minutes = bot_check_time_in_minutes ):
                if not hasSource( post ):
                    post.mod.remove()
                    printLog( "Post deleted." )
        printLog( "Sleeping for " + str( bot_sleep_time ) + " seconds...")
        sleep( bot_sleep_time )

if __name__ == "__main__":
    main()
