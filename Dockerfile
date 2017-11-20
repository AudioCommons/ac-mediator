FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64 && chmod +x /usr/local/bin/dumb-init

RUN mkdir /code
WORKDIR /code

# The following line copies a PIP configuration file to the container (if it exists).
# We use an internal PyPy mirror at the MTG and configure that at this step.
# Ideally we'd like to use some sort of "conditional ADD" statement here but Docker does not support that.
# As a workaround we use the wildcard so the file is added only if it is found.
ADD pip.* /etc/

ADD requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
ADD . /code/
RUN python manage.py collectstatic --no-input
WORKDIR /code/docs
RUN make clean html
WORKDIR /code
