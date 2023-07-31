#FROM python:3.9
FROM python:3.8-slim-bullseye

RUN apt-get update \
    && apt-get install -y wget gcc-10

# dependencies
RUN wget https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-codecs-ffmpeg_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb
RUN wget https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-codecs-ffmpeg-extra_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb

# chromium-browser
RUN wget https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-browser_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb

# chromium-chromedriver
RUN wget https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-chromedriver_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb

# Install all
RUN apt-get install -y ./chromium-codecs-ffmpeg_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb
RUN apt-get install -y ./chromium-codecs-ffmpeg-extra_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb
RUN apt-get install -y ./chromium-browser_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb
RUN apt-get install -y ./chromium-chromedriver_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb


RUN rm -rf /var/lib/apt/lists/*

RUN rm -f ./*.deb

RUN ln -s /usr/bin/gcc-10 /usr/bin/gcc

# Install selenium
RUN pip install -U pip
RUN pip install selenium paramiko
RUN pip install django django-apscheduler


EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]