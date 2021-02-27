# recipe-book
Python RESTFul API using Flask and SQLAlchemy

- SQLite as database

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


### This project was based on the book
##### Python API Development Fundamentals - By Jack Chan, Ray Chung, Jack Huang (Nov/2019)
