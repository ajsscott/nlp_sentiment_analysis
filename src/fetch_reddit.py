import os
import praw
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

# load environment
load_dotenv()

# initialize
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

# confirm folder
if not os.path.exists("data"):
    os.makedirs("data")

# subreddits
subreddits = [
	"union",
	"nursing",
	"Conservative",
	"liberal",
	"Libertarian",
	"progressive",
	"Ask_Politics",
	"antiwork",
	"WorkReform",
	"Strikes",
	"work",
	"Jobs",
	"OccupyWallStreet", s
	"MinimumWage",
	"BlueCollarWomen",
	"Teachers",
	"Truckers",
	"Construction",
	"LegalAdvice",
	"politics",
]

# timestamp
year = int((datetime.now() - timedelta(days=365)).timestamp())

# keywords
keywords = ["union", "strike", "labor", "worker", "workplace", "job"]

# posts with keywords
all_posts = []
for name in subreddits:
    try:
        subreddit = reddit.subreddit(name)
        print(f"Fetching posts from r/{name}")
        time.sleep(5)

        for post in subreddit.new(limit=1000):
            if post.created_utc >= year:
                # check for keywords
                content = f"{post.title} {post.selftext or ''}".lower()

                if any(word in content for word in keywords):
                    # posts
                    post_data = {
                        "subreddit": name,
                        "post_id": post.id,
                        "title": post.title,
                        "content": post.selftext if post.selftext else "[deleted]",
                        "score": post.score,
                        "created": datetime.fromtimestamp(post.created_utc),
                        "url": post.url,
                        "comments": [],
                    }

                # comments
                post.comments.replace_more(limit=0)
                for comment in post.comments.list()[:100]:  # fetch top 100 comments
                    post_data["comments"].append(
                        {
                            "comment_id": comment.id,
                            "content": comment.body if comment.body else "[deleted]",
                            "score": comment.score,
                            "created": datetime.fromtimestamp(comment.created_utc),
                        }
                    )

                all_posts.append(post_data)
    except Exception as e:
        print(f"Error fetching r/{name}: {e}")

# as df save to .csv
posts = []
comments = []

for post in all_posts:
    posts.append(
        {
            "subreddit": post["subreddit"],
            "post_id": post["post_id"],
            "title": post["title"],
            "content": post["content"],
            "score": post["score"],
            "created": post["created"],
            "url": post["url"],
        }
    )

    for comment in post["comments"]:
        comments.append(
            {
                "subreddit": post["subreddit"],
                "post_id": post["post_id"],
                "comment_id": comment["comment_id"],
                "content": comment["content"],
                "score": comment["score"],
                "created": comment["created"],
            }
        )

pd.DataFrame(posts).to_csv("data/posts3.csv", index=False)
pd.DataFrame(comments).to_csv("data/comments3.csv", index=False)

print(f"Saved {len(posts)} posts and {len(comments)} comments to CSV files.")
