# ScrapyKeeper

[![Latest Version](http://img.shields.io/pypi/v/SpiderKeeper.svg)](https://pypi.python.org/pypi/SpiderKeeper)
[![Python Versions](http://img.shields.io/pypi/pyversions/SpiderKeeper.svg)](https://pypi.python.org/pypi/SpiderKeeper)
[![The MIT License](http://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/DormyMo/SpiderKeeper/blob/master/LICENSE)
   
A scalable admin ui for scrapy spider service 

ScrapyKeeeper is a fork of [SpiderKeeper](https://github.com/DormyMo/SpiderKeeper)

Forked to provide:
  - Enhanced statistics (Errors, Exceptions, Retries...)
  - Cache support
  - Dashboarding
  - Most of pending SpideKeeper ahead commits

## Screenshot
![job dashboard](https://raw.githubusercontent.com/fliot/ScrapyKeeper/master/screenshot/screenshot_1.png)
![periodic job](https://raw.githubusercontent.com/fliot/ScrapyKeeper/master/screenshot/screenshot_2.1.png)
![project stats](https://raw.githubusercontent.com/fliot/ScrapyKeeper/master/screenshot/screenshot_3.png)
![spider stats](https://raw.githubusercontent.com/fliot/ScrapyKeeper/master/screenshot/screenshot_4.png)

How to install ?
```sh
git clone https://github.com/fliot/ScrapyKeeper.git
cd ScrapyKeeper
pip install .
```

Running:
```sh
scrapykeeper -h

Usage: scrapykeeper [options]

Admin ui for scrapy spider service

Options:
  -h, --help            show this help message and exit
  --host=HOST           host, default:0.0.0.0
  --port=PORT           port, default:6666
  --username=USERNAME   basic auth username ,default: admin
  --password=PASSWORD   basic auth password ,default: admin
  --type=SERVER_TYPE    access spider server type, default: scrapyd
  --server=SERVERS      servers, default: ['http://localhost:6800']
  --database-url=DATABASE_URL
                        ScrapyKeeper metadata database default: sqlite://./ScrapyKeeper.db
  --no-auth             disable basic auth
  --no-sentry           disable sentry.io error reporting
  -v, --verbose         log level
```
