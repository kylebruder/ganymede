# ganymede

Import well data into the app and create analysis reports and meta-reports based on user criteria.

## Settings.py
Included are two templates
* wells/settings.py.dev
* wells/settings.py.pro

Its best to configure the settings for your specific needs. These files are included as a suggested configuration for development and production environments respectively.

## Gunicorn
Gunicorn files are included
* gunicorn_start
* services/gunicorn.service

Use only for production. 

## Instructions for linux using systemd

Copy services/gunicorn.service to /etc/systemd/system/.
cp services/gunicorn.service /etc/systemd/system/gunicorn.service
Set the owner and permissions to root 655
sudo chown root:root /etc/systemd/system/gunicorn.service
Start and enable the gunicorn service
sudo systemctl start gunicorn && sudo systemctl enable gunicorn
