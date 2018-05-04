COAG Dashboard Install README
=============================

This is taken from Shane's Google Docs instructions.

I will gradually clean it up and convert to proper markdown.

```
OS USED: Ubuntu 16.04
REQUIREMENTS:
Python 2.7
PIP
Postgresql 9.6
PostGIS
Yarn
Node.js & npm
BUILD STEPS:
    DB:
sudo -u postgres psql
CREATE USER db_username_here WITH PASSWORD ‘db_password_here’;
CREATE DATABASE db_name_here WITH OWNER db_username_here;
\c db_name_here
CREATE EXTENSTION postgis;
\q
 
    API:
Clone openboard: https://bitbucket.csiro.au/projects/OPB/repos/openboard/browse
Checkout openboard ‘coag_performance’ branch
cd openboard/dashboard_api
pip install -r requirements.txt
cd dashboard_api
cp example_settings.py settings.py
Edit settings.py to reflect database/environment.
cd ..
python manage.py migrate


    Loader:
Clone openboard: https://bitbucket.csiro.au/projects/OPB/repos/openboard/browse
cd openboard/dashboard_loader
pip install -r requirements.txt
cd dashboard_loader
cp example_settings.py settings.py
Edit settings.py to reflect database/environment.
cd ..
python manage.py migrate
python manage.py import_data coag_uploader/exports/*.json
python manage.py register_loaders
python manage.py upload_all


    Front End:
Clone coag-frontend: https://bitbucket.csiro.au/projects/OPB/repos/coag-frontend/browse
cd coag-frontend
Edit environment.ts to fix path for api base and frontend base (relative paths should work)
yarn install
yarn run build:coag (I needed to edit the tsconfig.json. In case the repo does not get updated with a fix, or the change that I used: i needed to add "allowSyntheticDefaultImports": true to the compilerOptions object.)

APACHE setup:
apt-get install apache2
apt-get install libapache2-mod-wsgi
a2enmod wsgi
a2enmod rewrite
Copy coag-frontend/build/coag/* to /var/www/html/
Use the following in place of /etc/apache2/sites-available/000-default.conf
(This assumes you have checked out the repositories to /git/*. If not, adjust the paths as needed)

<VirtualHost *:80>

  WSGIDaemonProcess coag user=www-data group=www-data
  WSGIScriptAlias /api /git/openboard/dashboard_api/dashboard_api/wsgi.py
  DocumentRoot /git/coag-frontend/build/coag

  RewriteEngine  on

  <Location /api>
    WSGIProcessGroup coag
  </Location>

  <Location />
    RewriteEngine on
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteRule . /index.html [L]
  </Location>

  <Directory /git/openboard/dashboard_api/dashboard_api>
    <Files wsgi.py>
      AllowOverride None
      Require all granted
    </Files>
  </Directory>

  <Directory /git/coag-frontend/build/coag>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride All
    Require all granted
  </Directory>

</VirtualHost>

service apache2 restart
Note: For this to work I needed to comment out the entire “CACHES:” section of openboard/dashboard_api/dashboard_api/settings.py (lines 58 to 63)

```
