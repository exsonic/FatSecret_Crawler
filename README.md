Crawler for FatSecret.com
=========================
Bobi Pu, bobi.pu@usc.edu
------------------------



BEFORE RUN, PLEASE INSTALL:
===========================

1.MongoDB on your local host, and use FatSecret as your db name.

2.mechanize package.

3.beautifulsoup package.

4.FatSecret account, input your username and password in DataExtractor.py, login method.(line 34)




HOW TO RUN:
===========

1.In the terminal console, change your current directory to source code folder.

2.Execute command:`python DBController.py`. It will load the users to MongoDB database.

3.Execute command:`python crawl.py --help`. It will show your how to run the crawler.

4.Execute command:`python export.py --help`. It will show you how to export the data from databse. 



Note:
====
1.Crawling system is runing in multi-thread. Currently support 100 thread(hardcoded).

2.The exported data file will be in csv format and output to current folder.
