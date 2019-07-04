#
# Dockerfile for scrapyd:py3
#

FROM ubuntu:bionic

RUN set -xe \
    && apt-get update \
    && apt-get install -y autoconf \
                          build-essential \
                          curl \
                          git \
                          libffi-dev \
                          libssl-dev \
                          libtool \
                          libxml2 \
                          libxml2-dev \
                          libxslt1.1 \
                          libxslt1-dev \
                          python3 \
                          python3-dev \
                          python3-distutils \
                          vim-tiny \
                          zlib1g \
                          zlib1g-dev \
                          sqlite3 \
    && curl -sSL https://bootstrap.pypa.io/get-pip.py | python3 \
    && pip install git+https://github.com/scrapy/scrapyd.git \
                   git+https://github.com/scrapy/scrapyd-client.git \
                   git+https://github.com/c-lorand/ScrapyKeeper.git \
    && curl -sSL https://github.com/scrapy/scrapy/raw/master/extras/scrapy_bash_completion -o /etc/bash_completion.d/scrapy_bash_completion \
    && echo "source /etc/bash_completion.d/scrapy_bash_completion" >> /root/.bashrc \
    && apt-get purge -y --auto-remove autoconf \
                                      build-essential \
                                      libffi-dev \
                                      libssl-dev \
                                      libtool \
                                      libxml2-dev \
                                      libxslt1-dev \
                                      python3-dev \
    && apt-get purge -y --auto-remove libtiff5-dev \
                                      libfreetype6-dev \
                                      libjpeg-turbo8-dev \
                                      liblcms2-dev \
                                      libwebp-dev \
                                      zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 5000

CMD ["scrapykeeper", "--no-auth"]
