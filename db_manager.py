from pymongo import MongoClient
import pymongo

import os
import sys

# get database connection
def getConnection():
	# connect to local server
	client = MongoClient()	

	# connect to remote server
	#client = MongoClient("mongodb://mongodb0.example.net:27019") 

	# use a database named 'like123'
	db = client.like123
	return db

# check if data has key or not and remove the special characters(',', '"')
# 		return data[key], if key is existed
#			return "", otherwise
def checkKey(data, key, second_key=""):
	# if key is existed
	if second_key == "" and key in data:
			temp = data[key].replace(",", " ")
			temp = temp.replace("\"", " ")
			return temp
	elif second_key != "" and key in data and second_key in data[key]:
			temp = data[key][second_key].replace(",", " ")
			temp = temp.replace("\"", " ")
			return temp
	# otherwise
	else:
			return ""

# read data from mongodb database and write them into a file with csv format.
def CSVFile():

	# open csv file
	fp = open("data.csv", 'w')

	# write header in csv file
	fp.write('"Product Name","Price","Posted Date","Product Description","Company Name","Contact Person","Street Address","City","Country/Region","Zip","Telephone","Mobile Phone","Fax"\n')

	# get a connection of mongodb database
	db = getConnection()

	# get data group by search key and write data into csv file
	cursor = db.product.find().sort([("search_key", pymongo.ASCENDING)])
	for document in cursor:
		
		line = '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"\n' % \
				(checkKey(document, 'name'), checkKey(document, 'price'), checkKey(document, 'posted_on'),\
				checkKey(document, 'description'), checkKey(document, 'company', 'company_name'),\
				checkKey(document, 'company', 'contact_person'), checkKey(document, 'company', 'street_address'),\
				checkKey(document, 'company', 'city'), checkKey(document, 'company', 'country/region'), checkKey(document, 'company', 'zip'),\
				checkKey(document, 'company', 'telephone'), checkKey(document, 'company', 'mobile_phone'), checkKey(document, 'company', 'fax'))

		# get python version
		python_version = sys.version_info.major

		# encode data string with utf8
		if python_version == 3:
				fp.write(line)
		else:
				fp.write(line.encode("utf8"))

	fp.close()

# read data from mongodb and write them into csv file
if __name__ == '__main__':

	CSVFile()

