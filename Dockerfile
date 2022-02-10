FROM python:3.9.5-slim-buster

ENV HOME /root
ENV APP_HOME /application/
ENV C_FORCE_ROOT=true
ENV PYTHONUNBUFFERED 1

RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# Install pip packages
ADD ./requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

# Download the necessary NLTK corpora
RUN python -m textblob.download_corpora


# Copy code into Image
ADD ./youtube_script_sieve/ $APP_HOME

# collect static files
RUN $APP_HOME/manage.py collectstatic
