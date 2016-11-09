# Audio Commons mediator

Mediator component of the Audio Commons Ecosystem.

**NOTE:** What's hosted here is work in progress, no functional component is provided yet.


# Development

The Audio Commons mediator is a web service written in Python 3 using the Django framework.
We use the PostgreSQL database backend with the JSON fields, therefore you'll need PostgreSQL >= 9.2 installed in your system. 

Running the following commands should set a local installation of the Audio Commons mediator up and running:

- Clone repository and cd into it
```
git clone git@github.com:AudioCommons/ac-mediator.git
cd ac_mediator
```

- Install requirements (we recommed using vrtualenv)
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

For the documentation style we use a customized version of the 
[Read the Docs sphinx theme](https://github.com/snide/sphinx_rtd_theme/blob/master/README.rst).
The customized theme is already bundled with this repository in
[docs/_themes/ac_sphinx_rtd_theme](https://github.com/AudioCommons/ac-mediator/tree/master/docs/_themes/ac_sphinx_rtd_theme),
but if you want to edit it, you'll need to get the source from 
[https://github.com/AudioCommons/sphinx_rtd_theme](https://github.com/AudioCommons/sphinx_rtd_theme) 
and follow instructions in there.


# License
Apache License 2.0
