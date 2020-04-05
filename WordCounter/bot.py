import praw
from datetime import datetime, timedelta
from time import sleep
import re
import string
import config

def print_log(message):
    print(datetime.now(), end = " ")
    print(message)

def count_words(submission):
    counter = {}
    submission.comments.replace_more(limit = None)
    for comment in submission.comments.list():
        text = comment.body.lower()

        # Delete hyperlinks
        text = re.sub(r"http[^ ]", "", text)
        text = re.sub(r"\[.*\](.*)", "", text)
        # Delete subreddit/user mentions
        text = re.sub(r"[ur]/[^ ]", "", text)
        # Delete other garbage - punctuation, etc
        text = re.sub(r"[{}]".format(string.punctuation), " ", text)

        words = text.split()
        # Count words in comment
        comment_counter = {x : words.count(x) for x in words}

        # Save to main counter
        for word in comment_counter:
            if word in counter:
                counter[word] += comment_counter[word]
            else:
                counter[word] = comment_counter[word]
    return counter

def main():
    print_log("Logging in...")
    reddit = praw.Reddit(client_id = config.bot_id, client_secret = config.bot_secret, password = config.bot_pwd, user_agent = config.bot_agent, username = config.bot_usr)
    print_log("Logged in...")

    # Load already checked submissions from archive
    with open("checked.txt", "r") as f:
        checked = f.read().split()

    submissions = [x for x in reddit.redditor(config.bot_redditor).submissions.new(limit = 20) if x.subreddit.display_name in config.bot_subreddit and x.id not in checked and datetime.now() - datetime.fromtimestamp(x.created_utc) >= timedelta(hours = config.bot_post_age_hours)]
    print_log("There's {} submissions to look at.".format(len(submissions)))

    for submission in submissions:
        counter = count_words(submission)

        # Save submission as checked
        checked.append(submission.id)

        counter = {k : v for k, v in sorted(counter.items(), key = lambda item: item[1], reverse = True) if v >= config.bot_min_count}
        if counter != {}:
            # Format message
            message_text = "### Summary for [{}](https://reddit.com/{})\n\n".format(submission.title, submission.id)
            message_text += "Word | Sum\n:--:|:--:\n"
            for k, v in counter.items():
                message_text += "{} | {}\n".format(k, v)
            message_text += "^(Any trouble? Message u/m4rzus)"

            reddit.redditor(config.bot_send_to).message("Summary for {}".format(submission.id), message_text)
            print_log("Sent summary of {}".format(submission.title))

    # Archive checked submissions
    with open("checked.txt", "w") as f:
        f.write("\n".join(checked))

if __name__ == "__main__":
    while True:
        main()
        sleep(60 * 60 * 2) # Bot will awake every 2 hours
