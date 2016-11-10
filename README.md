# Audio Commons mediator

Mediator component of the Audio Commons Ecosystem.

**NOTE:** What's hosted here is work in progress, no functional component is provided yet.


# Development

The Audio Commons mediator is a web service written in Python 3 using 
the Django framework. We use the PostgreSQL database backend with the 
JSON fields (PostgreSQL >= 9.2).

To have a local development version you can either do a standard manual
install or use our Docker container definitions. When using Docker, the
development environment includes PostgreSQL, an Nginx webserver and the 
Django application running behind Gunicorn. It also includes custom SSL
certificates to be able to properly test the API via https. Below you'll
find instructions for setting up the development environment with and
without Docker:


## Setting up dev environment using Docker

- Clone repository and cd into it
```
git clone git@github.com:AudioCommons/ac-mediator.git
cd ac_mediator
```

- Rename ac_mediator/local_settings.example.py
```
cp ac_mediator/local_settings.example.py ac_mediator/local_settings.py
```

- Build and run Docker containers for required services
```
docker-compose build
docker-compose up
```

- You'll probably want to create a superuser too:
```
docker-compose run web python manage.py createsuperuser
```

Now you should be able to access your server at `https://localhost`


## Setting up dev environment without Docker

First you should make sure that you have PostgreSQL (>=9.2) installed and
running in your system. Then the following commands should set a local 
installation of the Audio Commons mediator up and running:

- Clone repository and cd into it
```
git clone git@github.com:AudioCommons/ac-mediator.git
cd ac_mediator
```

- Rename ac_mediator/local_settings.example.py
```
cp ac_mediator/local_settings.example.py ac_mediator/local_settings.py
```

- Install requirements (we recommend using virtualenv)
```
pip install -r requirements.txt
```

- Create database
```
createdb ac_mediator
python manage.py migrate
```

- Create super user
```
python manage.py createsuperuser
```

- Run service (and access it at `http://localhost:8000`)
```
python manage.py runserver
```


# Documentation

Documentation is located in the `docs` folder and can generated using Sphinx:
```
cd docs
make clean html
```

If you're using Docker you'll need to run these commands from the container:
```
docker-compose run web bash -c "cd docs && make clean html"
```


For the documentation style we use a customized version of the 
[Read the Docs sphinx theme](https://github.com/snide/sphinx_rtd_theme/blob/master/README.rst).
The customized theme is already bundled with this repository in
[docs/_themes/ac_sphinx_rtd_theme](https://github.com/AudioCommons/ac-mediator/tree/master/docs/_themes/ac_sphinx_rtd_theme),
but if you want to edit it, you'll need to get the source from 
[https://github.com/AudioCommons/sphinx_rtd_theme](https://github.com/AudioCommons/sphinx_rtd_theme) 
and follow instructions in there.


# License
Apache License 2.0
