import os
import random
import sys
import parse_testing_data
import re

#this is where the R image of the models should be
training_directory = '/home/max/workspace/webclass/keyword_training/'
#this is where the entire set of data should be
testing_directory = '/home/max/workspace/webclass/webpages/'
#classifications are done in blocks of 1000 in order to not use too much memory
block_size = 500
#will reach out to extra elements if the next set of data would have too few entries (for DF calculation purposes)
#note that later a universal DF should be calculated
block_final_reach = 250

def chunks(l, n, r = block_final_reach):
    """Yield successive n-sized chunks from l. Reach out up to r extra at end"""
    ll = len(l)
    for i in xrange(0, ll, n):
    	if ll - i -n < r:
    		yield l[i:i+n+r]
    		break
        yield l[i:i+n]

def main(args):
	#first partition file names into groups of several different files
	random.seed('default')
	webpage_list = [testing_directory + x for x in os.listdir(testing_directory)]
	webpage_list = [x for x in webpage_list if re.match('.*html$',x) <> None]
	random.shuffle(webpage_list)
	print 'loaded and shuffled filenames'
	#puts the webpages into blocks
	webpage_blocks = [x for x in chunks(webpage_list,block_size)]
	print 'classifying ' + str(len(webpage_blocks)) + ' blocks of data'
	for i, block in enumerate(webpage_blocks):
		parse_testing_data.analyze_webpages(block,i)














if __name__=='__main__':
	main(sys.argv[1:])