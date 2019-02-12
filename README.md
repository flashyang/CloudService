# CloudService

· Language(s): Front end is React + Backend is Python 
		     
· Frameworks: Flask

· Development and production web server:  Flask build-in. NGINX

· Testing frameworks: unittest module built in to the Python standard library. 

· Persistent Storage: mySQL

· Caching: Redis

· API technology: REST






# Command Line for running:

pip install -e .

(outside of the flaskr folder)

export FLASK_APP=flaskr

export FLASK_ENV=development

flask run

export FLASK_APP=flaskr

export FLASK_ENV=development

flask init-db


# Add gitignore
terminal在根目录下

touch .gitignore

打开.gitignore输入*.pyc

如果已经出现了pyc，就在terminal根目录下输入find . -name "*.pyc" -exec git rm -f "{}" \;



# Github clone and push:

git clone https://github.com/flashyang/CloudService.git

cd CloudService

git add -A

git commit -m "something"

git push -u 或者

git push -u origin master
