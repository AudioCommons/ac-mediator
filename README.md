# Audio Commons mediator

Mediator component of the Audio Commons Ecosystem.

**Note:** What's hosted here is work in progress, no functional component is provided yet.


# Development

The Audio Commons mediator is a web service written in Python 3 using
the Django framework. We use the PostgreSQL database backend with the
JSON fields (PostgreSQL >= 9.2), and also use a Redis store for managing
async operations.

The easiest way to set up a local development version is to use Docker
container definitions provided in this repository. When using Docker, the
development environment includes PostgreSQL, an Nginx web server, the Redis
data store and the Django application running behind Gunicorn.
It also includes custom SSL certificates to be able to properly test the
API via https. Below you'll find instructions for setting up the development
environment using Docker. You can also set up the development environment
manually by installing all dependencies (including PostgreSQL and Redis).
This works like a standard Django application but you'll have to manually
connect all components. We do not instructions for this but it should not be
too complicated.

## Setting up dev environment

Before starting make sure you have [Docker](https://www.docker.com/products/overview)
(with `docker-compose`) installed.

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
docker-compose up
```

- You'll probably want to create a superuser too:
```
docker-compose run web python manage.py createsuperuser
```

Now you should be able to access your server at `https://localhost`


**Note on API development:** to facilitate API development, unauthenticated
requests to the API are allowed when running ac-mediator locally. 
This behaviour can be changed editing the `ALLOW_UNAUTHENTICATED_API_REQUESTS_ON_DEBUG`
setting in `ac_mediator/settings.py`.


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
