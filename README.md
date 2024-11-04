# something-awesome-project
COMP6441 password manager
---
Overview
**A password manager that securely stores credentials to websites taking, managing URLs, usernames and passwords. To access the database, the project calls for a master password to authenticate the user. 
**---
Infrastructure

set up docker 
- make sure to have docker downloaded onto your desktop: https://www.docker.com/
---
to build the image: docker build -t password_manager .     
to run the program: docker run -p 5001:5000 password_manager
--- 
to run the main file: "./main.py" with selected inputs as defined by the argparser
- 
