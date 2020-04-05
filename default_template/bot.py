import praw
from datetime import datetime
from time import sleep

def print_log(message):
    print(datetime.now(), end = " ")
    print(message)

def main():
    print_log("Logging in...")
    reddit = praw.Reddit("BOT")
    print_log("Logged in...")

if __name__ == "__main__":
    main()
