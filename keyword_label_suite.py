from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import re
import csv

BASE_DIRECTORY = '/home/max/workspace/webclass/keyword_training/'





driver = webdriver.Firefox()
os.chdir(BASE_DIRECTORY)
files = [f for f in os.listdir(os.getcwd()) if re.match('.*html$',f) <> None]
print files
keyfiles = [f + '.key' for f in files]
numbers = [int(re.sub('[^0-9]*','',f)) for f in files]
print numbers

url_dict = dict()

with open('../webpages/id_url.txt','rb') as id_file:
	reader = csv.reader(id_file)
	for row in reader:
		if int(row[0]) in numbers:
			url_dict[int(row[0])] = row[1]


for number, keyfile, fn in zip(numbers,keyfiles,files):
	print keyfile
	print fn
	url = url_dict[number]
	size = os.stat(keyfile).st_size
	if size > 16:
		continue
	f = open(keyfile,'a')
	driver.get('http://' + url)
	
	while True:
		text = raw_input("ENTER KEYWORD/PHRASE: ")
		if text <> '':
			f.write(text + '\n')
		else:
			break
	f.close()
print 'done'
driver.close()

