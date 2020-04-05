import praw
from datetime import datetime
from time import sleep
import sqlite3
import schedule
import config

def print_log(message):
    print(datetime.now(), end = " ")
    print(message)

def generate_reply(comment = None, results = None):
    # Generate new reply
    if results is None and comment is None:
        message = "*Beep boop* Rate this shitpost by replying to me with either of these:\n\n"
        message += ", ".join(["\"" + x + "\"" for x in config.bot_choices])
        message += "\n\n^~\n\n*Results will be shown here*\n\n^~\n\n^(This post will be updated automatically every {} hours for {} days.)".format(config.bot_update, config.bot_max_age)
        return message

    # Generate updated reply
    else:
        body = comment.body.split("~") # Split comment into 3 sections - header, table with results, footer
        sorted_results = {k : v for k, v in sorted(results.items(), key = lambda item: item[1], reverse = True)} # Sort given results
        table = "**Results** | |\n:--: | :--: \n" # Generate table header
        # Add results into table, first bold
        it = iter(sorted_results.items())
        first_item = next(it)
        table += "**{}** | **{}**\n".format(*first_item)
        for item in it:
            table += "{} | {}\n".format(*item)
        body[1] = "\n\n" + table + "\n" # Insert table into its section
        return "~".join(body)

def save_new_posts(reddit, db):
    cur = db.cursor()
    sql = "SELECT pid FROM comments ORDER BY id DESC LIMIT 100;"
    cur.execute(sql)
    saved = [x[0] for x in cur.fetchall()]

    submissions = [x for x in reddit.subreddit(config.bot_subreddit).new(limit = 20) if x.link_flair_text == config.bot_flair and x.id not in saved]

    for submission in submissions:
        comment = submission.reply(generate_reply()) # Reply to submission
        comment.mod.distinguish(sticky = True) # Sticky comment
        print_log("Submission id {} commented, comment id: {}".format(submission.id, comment.id))

        sql = "INSERT INTO comments(cid, pid, age) VALUES(\"{}\", \"{}\", datetime('now'));".format(comment.id, submission.id)
        cur.execute(sql)
        print_log("Comment id {} saved into the database.".format(comment.id))


    if len(submissions) > 0:
        db.commit()
        print_log("All new submissions saved!\n" + "=" * 20)

def update_posts(reddit, db):
    # Load ids of all comments that are supposed to be updated
    cur = db.cursor()
    sql = "SELECT cid FROM comments WHERE age >= datetime('now', '-{} days');".format(config.bot_max_age)
    cur.execute(sql)
    saved = [x[0] for x in cur.fetchall()]

    for c_id in saved:
        comment = reddit.comment(id = c_id).refresh() # Get comment
        results = {x : 0 for x in config.bot_choices} # Dictionary for results

        already_voted = [] # List of redditors who already voted
        for choice in config.bot_choices:
            votes = set([x.author for x in comment.replies if choice.lower() in x.body.lower() and x.author not in already_voted]) # Set (to avoid multiple votes) of redditors who voted with this choice
            results[choice] = len(votes) # Set result for the choice
            already_voted += votes # Save redditors to avoid various votes by the same redditor

        comment.edit(generate_reply(comment, results)) # Edit comment with new generated reply
        print_log("Comment id {} updated.".format(comment.id))

    print_log("All comments updated!\n" + "=" * 20)

def main():
    print_log("Logging in...")
    reddit = praw.Reddit(client_id = config.bot_id, client_secret = config.bot_secret, password = config.bot_pwd, user_agent = config.bot_agent, username = config.bot_usr)
    db = sqlite3.connect("database.sql")
    print_log("Logged in...")

    schedule.every().minute.do(save_new_posts, reddit, db)
    schedule.every(config.bot_update).hours.do(update_posts, reddit, db)
    schedule.run_all()

    while True:
        schedule.run_pending()
        sleep(10)

if __name__ == "__main__":
    main()
