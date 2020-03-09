# ganymede
Import well data into the app and create analysis reports and meta-reports based on user criteria.

## Settings.py
settings.py is ignored in this repository for security reasons. Included are three example settings.py files
* wells/settings.py.dev
* wells/settings.py.pro

These settings are configured for use with postgreSQL server runing on the localhost and are included as a suggested configuration for development and production environments respectively. You must configure the database credentials.

For sqlite use:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

```
See https://github.com/django/django/blob/master/django/conf/project_template/project_name/settings.py-tpl and https://docs.djangoproject.com/en/3.0/ref/settings/ for more information

Development:
```bash
cp services/settings.py.dev wells/settings.py
```
Production:
```bash
cp services/settings.py.pro wells/settings.py
```
Using sym links works well if required.

## Gunicorn
Gunicorn files are included
* gunicorn_start
* services/gunicorn.service

Use only for production. 

### Instructions for linux using systemd

Copy services/gunicorn.service to /etc/systemd/system/.
```bash
cp services/gunicorn.service /etc/systemd/system/gunicorn.service
```
Set the owner and permissions to root 655
```bash
sudo chown root: /etc/systemd/system/gunicorn.service
```
Start and enable the gunicorn service
```bash
sudo systemctl start gunicorn && sudo systemctl enable gunicorn
```

## Nginx
Sample Nginx configuration is included
* services/ganymede.conf


