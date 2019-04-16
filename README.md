# CloudService (Team SocialPig)

· Language(s): Front end is HTML Ajax + Backend is Python Flask

· Development and production web server:  Flask build-in and NGINX with Gunicorn

· Testing frameworks: unittest module built in to the Python standard library. 

· Persistent Storage: mySQL (ClearDB)

· Caching: Redis

· API technology: REST

· Pipline: Jenkins

# Additional Url

· Host: http://ec2-3-85-103-162.compute-1.amazonaws.com

# Set up clearDB (MySQL database) on Heroku
```shell
brew install heroku/brew/heroku

heroku login

heroku create

heroku addons:create cleardb:ignite -a quiet-inlet-97604

heroku config -a quiet-inlet-97604 | grep CLEARDB_DATABASE_URL

pip install PyMySQL


testing database:

heroku addons:create cleardb:ignite -a fast-reaches-11674

heroku config -a fast-reaches-11674 | grep CLEARDB_DATABASE_URL
```



# Command Line for running:
Flask activate the vitual environment:
python3 -m venv venv

. venv/bin/activate

pip install -e .

(outside of the project folder)

export FLASK_APP=groupnest

export FLASK_ENV=development

pip install -r ./requirements.txt

export DATABASE_URL=mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330

export TEST_DATABASE_URL=mysql://b51ab60be50de0:b0ddd521@us-cdbr-iron-east-03.cleardb.net/heroku_36faaceaabbea7e

flask init-db

flask run


git pull origin yangsun



