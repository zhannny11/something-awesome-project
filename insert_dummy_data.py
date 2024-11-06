import sqlite3
import random
import master_password
import main

# Connect to your SQLite database
db_name = "/app/data/password.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# List of popular websites for URLs
urls = [
    "https://www.google.com",
    "https://www.amazon.com",
    "https://www.facebook.com",
    "https://www.youtube.com",
    "https://www.twitter.com",
    "https://www.instagram.com",
    "https://www.linkedin.com",
    "https://www.github.com",
    "https://www.reddit.com",
    "https://www.pinterest.com",
    "https://www.stackoverflow.com",
    "https://www.netflix.com",
    "https://www.paypal.com",
    "https://www.dropbox.com",
    "https://www.trello.com",
    "https://www.slack.com",
    "https://www.quora.com",
    "https://www.airbnb.com",
    "https://www.medium.com",
    "https://www.zapier.com",
    "https://www.zoom.us",
    "https://www.bitbucket.org",
    "https://www.gitlab.com",
    "https://www.mailchimp.com",
    "https://www.figma.com",
    "https://www.wix.com",
    "https://www.shopify.com",
    "https://www.walmart.com",
    "https://www.bbc.com",
    "https://www.nytimes.com",
    "https://www.cnn.com",
    "https://www.vimeo.com",
    "https://www.spotify.com",
    "https://www.apple.com",
    "https://www.microsoft.com",
    "https://www.twitch.tv",
    "https://www.ebay.com",
    "https://www.hulu.com",
    "https://www.adobe.com",
    "https://www.miro.com",
    "https://www.airtable.com",
    "https://www.notion.so",
    "https://www.xing.com",
    "https://www.yelp.com",
    "https://www.revolut.com",
    "https://www.etsy.com",
    "https://www.tinder.com",
    "https://www.wikipedia.org",
    "https://www.yahoo.com",
    "https://www.bestbuy.com"
]

# Sample emails as usernames
usernames = [
    "user1@example.com", "test.user@example.com", "example.user@gmail.com",
    "admin123@domain.com", "johndoe@example.com", "janedoe@example.com",
    "hello.world@example.com", "sample.user@yahoo.com", "another.email@gmail.com"
]

# Top 1000 common passwords (a small sample)
passwords = [
    "123456", "password", "123456789", "12345678", "12345", "qwerty",
    "abc123", "football", "monkey", "letmein", "1234", "passw0rd", "1234567"
]

# Generate and insert dummy data, ensuring unique URLs
for url in urls:
    # Check if the URL already exists in the table
    cursor.execute("SELECT 1 FROM passwords WHERE url = ?", (url,))
    if cursor.fetchone():
        print(f"URL '{url}' already exists, skipping.")
        continue

    # If the URL doesn't exist, insert it with a random username and password
    username = random.choice(usernames)
    password = random.choice(passwords)
    stored_hash, salt = master_password.retrieve_master_password(db_name)
    encrypted_password = main.encrypt_password(password, stored_hash, salt)
    cursor.execute("INSERT INTO passwords (url, username, password) VALUES (?, ?, ?)", (url, username, encrypted_password))

# Commit and close connection
conn.commit()
conn.close()

print("Dummy data inserted successfully.")
