### CommentVote

[screenshot](screenshot.png)

Simple vote system through comments. The bot comments on each submission with matching `bot_flair` (set in `config.py`) and updates the comment as redditors vote through replies on the comment.

In addition to `PRAW` module this bot requires also `sqlite3` and `schedule` modules (easily installable using `pip`).
