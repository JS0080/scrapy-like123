# Purposeful_Porpoise

1. Install packages

- Install Mongodb
	https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-14-04
- Install pymongo
	$ sudo pip install pymongo
- Install python scrapy
	$ sudo apt-get install python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
	$ pip install Scrapy

2. Run program
- In like123/, run the following command

	$ scrapy crawl like123

3. Result

- The program saves data into 'product' table in 'like123' database.
- data.csv in like123/

- command to export bson data from mongodb

	$ mongoexport --db like123 --collection product --out ./

- command to export json data from mongodb

	$ mongoexport --db like123 --collection product --out product.json

4. How to use jupyter

- Install jupyter package

* you have to use python 3 to use jupyter
$ sudo pip3 install jupyter

- Run jupyter server
In like123/, run the following command
$ jupyter notebook

- Notebooks
The project has two notebooks now: Like123Spider, Run Scrapy Program



