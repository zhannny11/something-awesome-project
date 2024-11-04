# something-awesome-project
COMP6441 password manager
---
Overview
A password manager that securely stores credentials to websites taking, and managing URLs, usernames and passwords. To access the database, the project calls for a master password to authenticate the user. 

---
Prerequisites
Install docker-desktop: https://www.docker.com/

---
Dependencies
bcrypt
pycryptodome
pbkdf2
watchdog

---
Setup
Step 1: Clone Project and Project Files
Clone the repository 
```
git clone <enter repository link>
cd something-awesome-project
```

Step 2: Generate a Master Password Hash
On 
On the first run, you’ll be prompted to set up a master password. This password will be securely hashed using bcrypt with a unique salt.


There are "two factors" of authentication included within the program. There are two options. You have to make sure the second_FA_location variable is either commented out or has a string inside the main.py program. If you do want to have a second factor of authentication, then you need to include hash the master_password_hash and the second_FA.

Enter the master password hash inside the master_password_hash variable inside the master_password.py program.

Step 3: Connect to Docker Container
Enter in correct username, database name, and password inside the db_connect.py file.

Step 4: Run Main.py
Run main.py with all files inside the same directory.

main.py [ARGUMENT] [OPTIONS}

Example to add Password: main.py -a https://cybercademy.org gcollins

Enter the one of the following paramters:

-a or --add [WEBSITE URL] [USERNAME]: Automatically generates a random 20 character string for password.
-q or --query [WEBSITE URL]: Look up field by website URL.
-l or --list: List all stored fields in password vault.
-d or --delete [WEBSITE URL]: Delete a field by website URL.
-ap or --add_password [WEBSITE_URL] [USERNAME] [PASSWORD]: Enter in a URL, username, and custom password.
-uurl or --update_url [NEW_URL] [OLD_URL]: Update the URL with new URL to currently stored URL.
-uuname or --update_username [URL] [NEW_USERNAME]: Update username of stored URL.
-upasswd or --update_password [URL] [NEW_PASSWORD]: Update new password by stored URL.


to build the image: docker build -t password_manager .   
to run the program: docker run -p 5001:5000 password_manager
--- 
to run the main file: "./main.py" with selected inputs as defined by the argparser
- 
