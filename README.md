# CloudService (Team SocialPig)

· Language(s): Front end is HTML + Backend is Python 
		     
· Frameworks: Flask

· Development and production web server:  Flask build-in. NGINX

· Testing frameworks: unittest module built in to the Python standard library. 

· Persistent Storage: mySQL

· Caching: Redis

· API technology: REST






# Command Line for running:
Flask activate the vitual environment:
python3 -m venv venv

. venv/bin/activate

pip install -e .

(outside of the project folder)

export FLASK_APP=groupnest

export FLASK_ENV=development

export DATABASE_URL=mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330

flask init-db

flask run


git pull origin yangsun


# Add gitignore
terminal在根目录下

touch .gitignore

打开.gitignore输入*.pyc

如果已经出现了pyc，就在terminal根目录下输入find . -name "*.pyc" -exec git rm -f "{}" \;



# Github clone and push:

git clone https://github.com/flashyang/CloudService.git
git clone -b yangsun https://github.com/flashyang/CloudService

cd CloudService

git add -A

git commit -m "something"

git push -u 或者

git push -u origin master

TODO:
1.	Facebook login - Stan
2.	Jenkins pipeline - yang sun
3.	Database - Qian
4.	Cache - Can
5.	Deploy NGix + WSGI – Yang Li

