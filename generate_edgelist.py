import re
import unicodecsv
import os
import sys

target_directory = '/home/max/workspace/webclass/webpages/'

default_directory = '/home/max/workspace/webclass/'

keyword_index = 'keyword_index.txt'
webpage_index = 'webpage_index.txt'
edgelist_output = 'keyword_edgelist.txt'

target_regex = '.*[0-9]{3}\.csv'

USE_OTHER_KEYWORD = True

#1. Read in all keyword files and create indexes for each webpage and ngram
#2. Re-scan each file and only keep keywords that still exist in master dictionary.

def main(args):
	os.chdir(target_directory)
	files = [x for x in os.listdir('.') if re.match(target_regex,x) <> None]
	master_dictionary = dict()
	website_dict = {}
	site_counter = 0
	nfiles = len(files)
	print 'got ' + str(nfiles) + ' filenames'
	for block_counter,filename in enumerate(files):
		#print "working with block # " + str(block_counter + 1)
		with open(filename,'rb') as f:
			reader = unicodecsv.reader(f)
			for line in reader:
				if line[0] not in website_dict:
					website_dict[line[0]] = site_counter
					site_counter += 1
				master_dictionary[line[1]] = master_dictionary.get(line[1],0) + 1
			reduce_dict_size(master_dictionary)
	if USE_OTHER_KEYWORD:
		master_dictionary["OTHER"] = 5
	print 'made main dictionary'
	print 'length of master_dictionary: ' + str(len(master_dictionary))
	print 'length of websites dictionary: ' + str(site_counter)
	#now generate indices
	indexed_dictionary = {name:index for index,name in enumerate(master_dictionary)}
	with open(keyword_index,'w') as kf:
		for name, index in indexed_dictionary.iteritems():
			kf.write(name + ','  + str(index) + '\n')
	with open(webpage_index,'w') as wf:
		for entry, index in website_dict.iteritems():
			wf.write(entry + ',' + str(index) + '\n')
	for filename in files:
		with open(filename,'rb') as f,  open(edgelist_output,'w') as edgefile:
			reader = unicodecsv.reader(f)
			reader.next()
			for line in reader:
				#print line
				web_i = website_dict[line[0]]
				if USE_OTHER_KEYWORD:
					gram_i = indexed_dictionary.get(line[1],indexed_dictionary['OTHER'])
				else:
					gram_i = indexed_dictionary.get(line[1],None)
				prob = str(round(float(line[2]),6))
				if gram_i <> None:
					edgefile.write(str(web_i) + ' ' + str(gram_i) + ' ' + str(prob) + '\n')
	print 'wrote edge files'



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






if __name__ == '__main__':
	main(sys.argv[1:])