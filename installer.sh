#!/usr/bin/env bash

# How to use this script.
# 1. Install git
# sudo apt-get install git;
# 2. Clone repo from github.
# git clone https://github.com/barbarossa22/td.git;
# 3. cd to cloned directory.
# cd td;
# 4. Add execute permissions to installer.sh script.
# sudo chmod 755 installer.sh;
# 5. Run this script with sudo.
# sudo ./installer.sh
# 6. Relax and wait.

_() { printf "\033[1;31m$1\033[0m \n"; }


###
_ "*** Initial setup on clean Ubuntu 14 ***";
##
#

_ "Reload the local package database:";
_ "sudo apt-get update;"
sudo apt-get update;
_ "Install package which includes additional header files, a static library";
_ "and development tools for building Python modules:";
_ "sudo apt-get install -y python-dev;"
sudo apt-get install -y python-dev;
_ "Get pip:";
_ "sudo apt-get install -y python-pip;";
sudo apt-get install -y python-pip;

_ "Install libffi package(Foreign Function Interface library) which is needed";
_ "for bcrypt python library.";
_ "sudo apt-get install libffi-dev";
sudo apt-get install libffi-dev

_ "Install ruby and it's gem SaSS";
_ "sudo apt-get install ruby;";
sudo apt-get install ruby;
_ "sudo gem install sass;";
sudo gem install sass;


###
_ "*** Setup databases*** ";
##
#

##
_ "** MySQL **";
#

_ "Install mysql-server package (on root password creation prompt, please,";
_ "provide password easy to recall later):";
_ "sudo apt-get install -y mysql-server;";
sudo apt-get install -y mysql-server;
_ "Execute the included security script which changes some of the less secure";
_ "default options (you need to answer on all prompts):";
_ "sudo mysql_secure_installation;";
sudo mysql_secure_installation;
_ "Initialize the data directory:";
_ "sudo mysql_install_db;";
sudo mysql_install_db;

#To check if everything was installed properly you can run interactive"
#interpreter with next command:
#sudo mysql -u root -p
_ "In order to make future installations of python's MySQLdb less painful and";
_ "easy you need to install libmysqlclient-dev package which includes mysql";
_ "database development files.";
_ "sudo apt-get install -y libmysqlclient-dev;"
sudo apt-get install -y libmysqlclient-dev;

##
_ "** Postgresql **";
#

_ "Get the Postgres package and a "contrib" package that adds some additional";
_ "utilities and functionality:";
_ "sudo apt-get install -y postgresql postgresql-contrib;";
sudo apt-get install -y postgresql postgresql-contrib;
_ "Install libpq-dev library which contains binaries for installation and";
_ "proper work in future of psycopg2 (postgres adapter for python).";
_ "sudo apt-get install -y libpq-dev;";
sudo apt-get install -y libpq-dev;
#To check if everything was installed properly you can switch to postgres
# administrative user and run interactive interpreter with next commands:
#sudo -i -u postgres
#psql

##
_ "** Mongodb **";
#

_ "Import the public key used by the package management system:";
_ "sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6;";
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6;
_ "Create the /etc/apt/sources.list.d/mongodb-org-3.4.list list file:";
_ "echo \"deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse\" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list;";
echo "deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list;
_ "Reload the local package database:";
_ "sudo apt-get update;";
sudo apt-get update;
_ "Install the MongoDB packages:";
_ "sudo apt-get install -y mongodb-org;"
sudo apt-get install -y mongodb-org;
_ "Start mongod service:";
_ "sudo service mongod start;";
sudo service mongod start;
#To check if everything was installed properly you can run interactive
# interpreter with next command: mongo


##
_ "** Create users, databases and tables **";
#

#Run script from mysql (path to script given as example, you need to provide
# own path to it):
#mysql -u root -p;
#source /home/<user>/td/fixtures/create_mysql_db.sql;
_ "Create user, db and table in mysql.";
_ "mysql -u root -p < ~/td/fixtures/create_mysql_db.sql;";
mysql -u root -p --force < ~/td/fixtures/create_mysql_db.sql;


#Run script from postgres (path to script given as example, you need to provide
# own path to it):
#sudo -i -u postgres;
#psql;
#\i /home/<user>/td/fixtures/create_postgres_db.sql
_ "Create user, db and table in postgres.";
_ "sudo -u postgres psql < ~/td/fixtures/create_postgres_db.sql;";
sudo -u postgres psql < ~/td/fixtures/create_postgres_db.sql;

###
_ "*** virtualenvwrapper ***";
#

_ "Get virtualenvwrapper from pypi:";
_ "sudo pip install virtualenvwrapper;";
sudo pip install virtualenvwrapper;
_ "Append this to your user's ~/.bashrc file:";
_ "echo \"source /usr/local/bin/virtualenvwrapper.sh;\" >> ~/.bashrc";
echo "source /usr/local/bin/virtualenvwrapper.sh;" >> ~/.bashrc;
source /usr/local/bin/virtualenvwrapper.sh;

_ "Now you can create own virtual environment:";
_ "mkvirtualenv td;";
mkvirtualenv td;
_ "And work with it:";
_ "workon td;";
workon td;
_ "Use deactivate to exit current virtual environ, lsvirtualenv and";
_ "rmvirtualenv <name> to list all existing and remove single one by the name.";


###
_ "*** Pyramid app setup and start ***";
#

##
_ "** Install Python dependancies **";
#

#If you're not in the project's dir cd to it and then invoke command, which
# installs the project in development mode (-e is for "editable") into the
# current directory (.):
_ "pip install -e .;";
pip install -e .;
#It is just pip wrapping on python setup.py develop, so you can use it too.

#When you add new dependancies to the project the updates can be installed
# through usage of next commands: pip install -e . or python setup.py develop
# or pip install -r requirements.txt. The last one is the fastest way.

## Tests

_ "Install testing dependancies from setup.py 'tests_require' section:";
_ "pip install -e \".[testing]\";";
pip install -e ".[testing]";
#or you can do it directly from the file with command pip install -r test_requirements.txt

##
_ "** Create user to login the app. **";
#

## Postgres db:
#sudo -i -u postgres
#psql
#\c TDDB;
#insert into "Users" (id, ip, username, password, groups) values (1, '127.0.0.1', 'user', '$2b$12$/zC.07EVRZc3Qiyymhzcz.bWaJFKde0nepVpx6cZZowz0WQZ7Wp.W', 'group:users');
_ "Insert new app's user into pgres db.";
postgres_template="insert into \"Users\" (id, ip, username, password, groups) values (1, '127.0.0.1', 'user', '\$2b\$12$/zC.07EVRZc3Qiyymhzcz.bWaJFKde0nepVpx6cZZowz0WQZ7Wp.W', 'group:users');"
sudo -u postgres psql TDDB << EOF
$postgres_template;
EOF


## or Mysql db:
#mysql -u root -p
#use TDDB;
#insert into Users (id, ip, username, password, groups) values (1, '127.0.0.1', 'user', '$2b$12$/zC.07EVRZc3Qiyymhzcz.bWaJFKde0nepVpx6cZZowz0WQZ7Wp.W', 'group:users');
_ "Insert new app's user into mysql db.";
mysql_template="insert into Users (id, ip, username, password, groups) values (1, '127.0.0.1', 'user', '\$2b\$12$/zC.07EVRZc3Qiyymhzcz.bWaJFKde0nepVpx6cZZowz0WQZ7Wp.W', 'group:users');"
mysql -u root -p TDDB << EOF
$mysql_template;
EOF

_ "Your username is user and password is 1234.";

_ "Compile stylesheets:";
_ "sass td/static/sass:td/static/stylesheets";
sass td/static/sass:td/static/stylesheets;

## Run

#Run the application with needed configuration file:
#pserve production.ini
#(production.ini doesn't work ofc. because it is not updated with current state
# of proj.)
#To run app with development config execute next command:
#pserve development.ini --reload;
#--reload option if used waits for any changes to any Python module and when
# they're detected causes the server to restart.
#Now app is accessible from the browser at address http://localhost:6543 or
# whatever path/port you provide inside your configs.


_ "Reboot your computer in 5 seconds.";
sleep 5;
sudo reboot;
