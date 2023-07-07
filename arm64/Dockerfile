FROM python:3.9

# Update on 2021/12/30

# dependencies
RUN wget https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-codecs-ffmpeg_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb
RUN wget https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-codecs-ffmpeg-extra_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb

# chromium-browser
RUN wget https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-browser_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb

# chromium-chromedriver
RUN wget https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files/chromium-chromedriver_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb

# Install all
RUN apt-get update

RUN apt-get install -y ./chromium-codecs-ffmpeg_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb
RUN apt-get install -y ./chromium-codecs-ffmpeg-extra_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb
RUN apt-get install -y ./chromium-browser_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb
RUN apt-get install -y ./chromium-chromedriver_90.0.4430.93-0ubuntu0.16.04.1_arm64.deb

# Install selenium
RUN pip install -U pip
RUN pip install selenium

RUN rm -f ./*.deb