FROM python:3.8.2

# デフォルトの locale `C` を `C.UTF-8` に変更する
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# タイムゾーンを日本時間に変更
ENV TZ Asia/Tokyo

RUN apt-get update && apt-get install -y unzip vim

#install google-chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

#install selenium
RUN pip3 install --upgrade pip && pip3 install selenium pandas beautifulsoup4==4.9.0

#install ChromeDriver
ADD https://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && \
    unzip chromedriver_linux64.zip

ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/chrome