# td
to-do list project playground

You can use `install.sh` shell script to run automated environment setup (see description in that file), otherwise follow steps below to prepare everything manually.

## Initial setup on clean Ubuntu 14


Reload the local package database:

`sudo apt-get update`

On clean ubuntu systems there is no in-built git so install it:

`sudo apt-get install git`

Install package which includes additional header files, a static library and development tools for building Python modules:

`sudo apt-get install python-dev`

Get pip:

`sudo apt-get install python-pip`

Install libffi package(Foreign Function Interface library) which is needed for bcrypt python library.

`sudo apt-get install libffi-dev`

## Setup databases

### MySQL

Install mysql-server package (on root password creation prompt, please, provide password easy to recall later):

`sudo apt-get install mysql-server`

Execute the included security script which changes some of the less secure default options (you need to answer on all prompts):

`sudo mysql_secure_installation`

Initialize the data directory:

`sudo mysql_install_db`

To check if everything was installed properly you can run interactive interpreter with next command:

`sudo mysql -u root -p`

In order to make future installations of python's MySQLdb less painful and easy you need to install libmysqlclient-dev package which includes mysql database development files.

`sudo apt-get install libmysqlclient-dev`

Install ruby and it's gem SaSS:

`sudo apt-get install ruby`

`sudo gem install sass`

### Postgresql

Get the Postgres package and a "contrib" package that adds some additional utilities and functionality:

`sudo apt-get install postgresql postgresql-contrib`

Install libpq-dev library which contains binaries for installation and proper work in future of psycopg2 (postgres adapter for python).

`sudo apt-get install libpq-dev`

To check if everything was installed properly you can switch to `postgres` administrative user and run interactive interpreter with next commands:

`sudo -i -u postgres`

`psql`

### Mongodb
Import the public key used by the package management system:

`sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6`

Create the /etc/apt/sources.list.d/mongodb-org-3.4.list list file:

`echo "deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list`

Reload the local package database:

`sudo apt-get update`

Install the MongoDB packages:

`sudo apt-get install -y mongodb-org`

Start mongod service:

`sudo service mongod start`

To check if everything was installed properly you can run interactive interpreter with next command: `mongo`



### Create users, databases and tables

Run script from mysql (path to script given as example, you need to provide own path to it):

`mysql -u root -p`

`source /home/<user>/td/fixtures/create_mysql_db.sql;`

Run script from postgres (path to script given as example, you need to provide own path to it):

`sudo -i -u postgres`

`psql`

`\i /home/<user>/td/fixtures/create_postgres_db.sql`


## virtualenvwrapper

Get virtualenvwrapper from pypi:

`sudo pip install virtualenvwrapper`

Append this to your user's ~/.bashrc file:

`source /usr/local/bin/virtualenvwrapper.sh`

Reboot your computer or just update your user's profile with `source ~/.bashrc`.

Now you can create own virtual environment:

`mkvirtualenv td`

And work with it:

`workon td`

Use `deactivate` to exit current virtual environ, `lsvirtualenv` and `rmvirtualenv <name>` to list all existing and remove single one by the name.



## Pyramid app setup and start

##### Install Python dependancies

If you're not in the project's dir cd to it and then invoke command, which installs the project in development mode (-e is for "editable") into the current directory (.):

`pip install -e .`

It is just pip wrapping on `python setup.py develop`, so you can use it too.

When you add new dependancies to the project the updates can be installed through usage of next commands: `pip install -e .` or `python setup.py develop` or `pip install -r requirements.txt`. The last one is the fastest way.

##### Create user to login the app.

Postgres db:

`sudo -i -u postgres`

`psql`

`\c TDDB;`

`insert into "Users" (id, ip, username, password, groups) values (1, '127.0.0.1', 'user', '$2b$12$/zC.07EVRZc3Qiyymhzcz.bWaJFKde0nepVpx6cZZowz0WQZ7Wp.W', 'group:users');`

or Mysql db:

`mysql -u root -p`

`use TDDB;`

`insert into Users (id, ip, username, password, groups) values (1, '127.0.0.1', 'user', '$2b$12$/zC.07EVRZc3Qiyymhzcz.bWaJFKde0nepVpx6cZZowz0WQZ7Wp.W', 'group:users');`

Your username is `user` and password is `1234`.

##### Compile stylesheets:

`sass --update td/static/sass:td/static/stylesheets`

Also you can add `--watch` to force sass autodetect and compile css output immediately after any updates to sass code.

##### Run

Run the application with needed configuration file:

`pserve production.ini` 

(production.ini doesn't work ofc. because it is not updated with current state of proj.)


To run app with development config execute next command:

`pserve development.ini --reload`

`--reload` option if used waits for any changes to any Python module and when they're detected causes the server to restart.

Now app is accessible from the browser at address `http://localhost:6543` or whatever path/port you provide inside your configs.


## Tests
Install testing dependancies from setup.py 'tests_require' section:

`pip install -e ".[testing]"` or you can do it directly from the file with command `pip install -r test_requirements.txt`

Use nosetests to autodiscover existing tests modules for the project and run them.

`nosetests`

To get info about coverage:

`nosetests --with-coverage`

## Documentation

You can use Sphinx to autogenerate html with code documentation. Make build from source files with (cd to project's root directory, if you're not there):

`sphinx-build -b html source build`

Now it's possible to read the docs opening them in `build/index.html` and then surfing in the browser through the pages.
