# recipe-book
Python RESTFul API using Flask and SQLAlchemy

- SQLite as database

### Installing the packages
If you are using PyCharm IDE, right after add your package to the requirements file, you will see the option 
"install requiriments" enabled, you just have to click there.

If you are not using PyCharm IDE, you can run the command

```
pip install -r requirements.txt
```

### Creating the database
- to initialize the database (after run the command below, a new folder called migrations will be created)
```
flask db init
```
- to create the database and tables
```
flask db migrate
```
- to upgrade the database
```
flask db upgrade
```
After run the commands above, it's possible to see a new file called **recipebook.db**, this is our database.
You can use DB Browser for SQLite to as GUI to access the database.


## How it works
### Creating and activating users
- "Add new user" endpoint

After create a new user, an email is sent with a activation link (in this code, I'm using the sandbox of mailgun, so 
only one email is registered).

- "Activate User" endpoint

After clicking in the link sent by email, the user will be activated 

---

### This project was based on the book
##### Python API Development Fundamentals - By Jack Chan, Ray Chung, Jack Huang (Nov/2019)
