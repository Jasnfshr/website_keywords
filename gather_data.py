import sys
import os
import urllib2
import re
import socket
import csv
from httplib import BadStatusLine,IncompleteRead,HTTPException

def remove_duplicates(obj):
	l = len(obj)
	for i in range(l-1, 0, -1):
		if obj[i] in obj[:(i-1)]:
			obj.pop(i)
	return obj

def fname(i):
	return 'webpage_' + str(i) + '.html'

def main():
	url_file = open('url_list.txt','r')
	urls = url_file.readlines()
	urls = [re.sub('\n','',url) for url in urls]
	urls = remove_duplicates(urls)
	print "LENGTH OF URL LIST: " + str(len(urls))
	os.chdir('webpages')
	current_files = [f for f in os.listdir('.') if os.path.isfile(f)]
	#write the urls
	f = open('id_url.txt','wb')
	cf = csv.writer(f)
	cf.writerows([[k, url] for k, url in enumerate(urls)])
	f.close()
	print 'wrote url id file'
	print 'number of urls: ' + str(len(urls))
	for k, url in enumerate(urls):
		attempts = 0
		if k < 21000:
			continue
		while attempts < 1:
			if fname(k) in current_files:
				print k
				break
			try:
				response = urllib2.urlopen('http://' + url,timeout=3)
				content = response.read()
				f = open(fname(k),'w')
				f.write(content)
				f.close()
				break
			except (HTTPException, socket.error, IncompleteRead, BadStatusLine, socket.timeout, urllib2.URLError) as e:
				attempts += 1
				print type(e)
				#print attempts
		if k % 100 == 0:
			print 'done with %s sites' % (str(k))
	print 'done'




if __name__ == '__main__':
	main()

