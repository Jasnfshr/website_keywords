import nltk
import nltk.data, nltk.tag
from nltk.tag.perceptron import PerceptronTagger
import sys
import os
from bs4 import BeautifulSoup
import re
import html_extract
import pickle
import csv
import numpy
import pandas
import copy
import argparse

#command line arguments:
#-nval

os.chdir('/home/max/workspace/webclass/keyword_training')

#variables needed
#word in hypertext
#log(TF + 1)
#log(DF + 1 (+1 for smoothing))
#relative position of word/phrase
#whether word/phrase appears in title
#whether word/(collapsed) phrase appears in URL


#steps

#1 
#scan through all documents and create a dictionary (that gets reduced occosionally)
#of all the terms
#*omit non-noun/adjective/verb words

nvals = [1,2]

def reduce_dict_size(d,max_size = 250000,cutoff=4,reducer=1):
	keys = d.keys()
	if len(keys) <=max_size:
		return False
	print 'reducing dict size'
	for key in keys:
		if d[key] < cutoff:
			d.pop(key)
		else:
			d[key] = d[key] - reducer
	return True

files = os.listdir('.')
training_files = [f for f in files if f[len(f)-1] == 'l']
key_files = [f for f in files if f[len(f)-1] == 'y']

print 'files loaded'

#initialize master dictionary
master_dict = dict()
for i in nvals:
	master_dict[i] = {}

#create document frequency dictionary
for f in training_files:
	information = html_extract.get_tf_information(f)
	for N,entry in information.iteritems():
		for key in entry:
			master_dict[N][key] = master_dict[N].get(key,0)+1
		reduce_dict_size(master_dict[N])

with open('document_frequencies.pickle','wb') as f:
	pickle.dump(master_dict,f)

print 'DF information extracted'

#2
#for each document, create all of the word-variable items and put them into a table
#use the document id as a reference variable, and store the values into
#a shelve file

numbers = [int(re.sub('[^0-9]*','',f)) for f in training_files]
url_dict = dict()
with open('../webpages/id_url.txt','rb') as id_file:
	reader = csv.reader(id_file)
	for row in reader:
		if int(row[0]) in numbers:
			url_dict[int(row[0])] = row[1]

training_dictionary = {}
print 'url data extracted'

#extract information from data sets
for num,f in zip(numbers,training_files):
	url = url_dict[num]
	training_dictionary[f] = html_extract.get_complete_information(f,nvals,url)

with open('training_data_intermediate.pickle','wb') as f:
	pickle.dump(training_dictionary,f)

print 'training data extracted'

#get the DF information for each word and add 1
#note that these training samples are going to be large
#in a production environment, the individual file dictionaries will 
#have to be run in blocks in order to avoid memory overload
for fil, training_samples in training_dictionary.iteritems():
	for nval, gram_dictionary in training_samples.iteritems():
		for entry in gram_dictionary:
			gram_dictionary[entry]['DF'] = master_dict[nval].get(entry,0) + 1

#pickle the object if something goes wrong
with open('training_data_final.pickle','wb') as f:
	pickle.dump(training_dictionary,f)

print 'training data finalized'

#for each entry in training data, check to see if an entry is in the keys
for filename in key_files:
	key = filename[:-4]
	f = open(filename,'r')
	keywords = [re.sub('\n','',x) for x in f.readlines()]
	training_samples = training_dictionary[key]
	for nval,gram_dictionary in training_samples.iteritems():
		for entry in gram_dictionary:
			gram_dictionary[entry]['is_keyword'] = 1*(entry in keywords)

with open('training_data_final_with_response.pickle','wb') as f:
	pickle.dump(training_dictionary,f)

print 'added response variables to model'


with open('training_data_final_with_response.pickle','rb') as f:
	training_dictionary = pickle.load(f)
	print 'training dictionary loaded'

master_frame = pandas.DataFrame(columns = ['file_id','gram','tf','df','in_url','in_title','in_hyperlink','pos','length','is_keyword']
	)
index = 0
temp_index = 0
frame_list = []
current_frame = copy.copy(master_frame)

for fil, training_samples in training_dictionary.iteritems():
	for nval, gram_dictionary in training_samples.iteritems():
		for entry,values in gram_dictionary.iteritems():
			current_frame.loc[temp_index] = [fil,entry,values['tf'],values['DF'],
			values['in_url'],values['is_title'],values['is_hyperlink'],values['pos'],nval,values['is_keyword']]
			index += 1
			temp_index += 1
			if index % 50000 == 0:
				print index
			if temp_index == 150:
				temp_index = 0
				frame_list.append(current_frame)
				current_frame = copy.copy(master_frame)
if temp_index <> 0:
	frame_list.append(current_frame)
master_frame = pandas.concat(frame_list)


column_dtypes = ['string','string','float','float','int','int','int','float','float','int']
for i, name in enumerate(master_frame):
	master_frame[name] = pandas.DataFrame(master_frame[name],dtype=column_dtypes[i])

with open('training_data_pandas_frame','wb') as f:
	pickle.dump(master_frame,f)

lmf = copy.copy(master_frame)

lmf['tf'] = numpy.log(1+lmf['tf'])
lmf['df'] = numpy.log(1+lmf['df'])
with open('keyword_data.csv','wb') as f:
	lmf.to_csv(f,encoding='utf-8')

print 'saved log-transformed frame to csv'

if '--analyze' in sys.argv:
	os.system('roc_analysis.r')


#for now I have delegated this to R since the task is easy enough once the data
#frame is cleaned
#3
#use logistic regression to predict the probability that
#a word/phrase would be considered a keyword for a page


#4
#store results and try practicing model on a test set, possibly by using
#cross-validation with another set, or maybe just doign it on pages and looking
#to see if the results are any good
