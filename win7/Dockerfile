#FROM python:3.9
FROM python:3.8-slim-bullseye
RUN apt-get update \
    && apt-get install -y python3-selenium

RUN rm -rf /var/lib/apt/lists/*

RUN rm -f ./*.deb


# Install selenium
RUN pip install -U pip
RUN pip install selenium paramiko
RUN pip install django django-apscheduler


EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]