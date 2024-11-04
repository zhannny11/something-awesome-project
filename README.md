# something-awesome-project

### COMP6441 password manager

---
### Overview
A password manager that securely stores credentials to websites taking, and managing URLs, usernames and passwords. To access the database, the project calls for a master password to authenticate the user. 

---
### Prerequisites
Install docker-desktop: https://www.docker.com/

Python 3.8 or higher

---
### Dependencies
- bcrypt
- pycryptodome
- pbkdf2
- watchdog

---
### Setup
**Step 1:** Clone Project and Project Files
Clone the repository.
```
git clone <enter repository link>
cd something-awesome-project
```
**Step 2:** Build and Run the Docker Container
Starts up all services located in the `docker-compose.yml` and `Dockerfile`.
Includes hot reloads (automatically applies code and database changes) and can use in conjunction with any arguments.

`-d`: loads in a detached manner
```
docker-compose up -d
```
Run the docker container with chosen arguments/flags.
```
docker-compose exec app
```
Here is an outline of the possible commands:
python main.py [ARGUMENT] {OPTIONS}

Enter one of the following paramters:

-a or --add [WEBSITE URL] [USERNAME]: Adds an entry and automatically generates a random 12 character and digit string as the password.

-q or --query [WEBSITE URL]: Look up entry by URL.

-l or --list: List all records detailing their the stored fields in the password manager.

-d or --delete [WEBSITE URL]: Delete a field by URL.

-ap or --add_password [WEBSITE_URL] [USERNAME] [PASSWORD]: Enter in a URL, username, and custom password.

-uurl or --update_url [NEW_URL] [OLD_URL]: Update URL within an entry.

-uuname or --update_username [URL] [NEW_USERNAME]: Update username within an entry.

-upasswd or --update_password [URL] [NEW_PASSWORD]: Update password given the URL.
e.g. Add credentials to the password manager by providing the url and user
```
docker-compose exec app python main.py -a "www.example.url.com" "test user"
```

**Step 3:** Closing the container
When you're done with the password manager
```
docker-compose down
```


