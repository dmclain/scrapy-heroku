Scrapy-Heroku
=============

A package to assist with running scrapy on heroku. This is accomplished by providing
a custom application configuration at ``scrapy_heroku.app.application`` that launches
the scrapyd web service using the PORT environment variable and a multi-process work
queue implemented on a Postgres database specified by the DATABASE_URL environment
variable.

Configuration
-------------

Create a git repo that has a scrapy project at the root (scrapy.cfg should be at the
top level). Edit your scrapy.cfg to include the following::

```python
[scrapyd]
application = scrapy_heroku.app.application

[deploy]
url = http://<YOUR_HEROKU_APP_NAME>.herokuapp.com:80/
project = <YOUR_PROJECT_NAME>
username = <A_USER_NAME>
password = <A_PASSWORD>
```

Add a requirements.txt file that includes ``scrapy``, ``scrapy-heroku``, and ``scrapyd``.
It is strongly recommended that you version pin scrapy-heroku as well as the version of scrapy that
your project is developed against (pip freeze > requirements.txt).

For Example:
```python
# requirements.txt
Scrapy==0.24.4
scrapyd==1.0.1
scrapy-heroku==0.7.1
```

Finally create a Procfile that consists of::

```
web: scrapyd
```

Make sure you have a postgres database with the DATABASE_URL env parameter set.


* Project page: <http://github.com/dmclain/scrapy-heroku>
