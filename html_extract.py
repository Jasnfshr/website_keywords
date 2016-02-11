import nltk
import nltk.data, nltk.tag
from nltk.tag.perceptron import PerceptronTagger
import sys
import os
from bs4 import Tag, BeautifulSoup
import bs4
import re
from nltk.corpus import stopwords as sw
import pickle

stopwords = sw.words('english')
stopwords = stopwords + ['the','of','for','at','do','or']


MAX_WORD_LENGTH = 30

word_validation_regex = r'[\w\-]{2,' + str(MAX_WORD_LENGTH) + r'}'

print 'word validationr regex: ' + word_validation_regex

stopwords = [word for word in stopwords if re.match(word_validation_regex,word) <> None]

print 'stopwords working: ' + str(all([x in stopwords for x in ['the','of','by']]))

#this allows keywords to be extracted from the title
#in terms of modelling, the inclusion of a title indicator variable should avoid
#the problem of having a low value for position (if you wanted to prepend instead)
append_title_to_body = True


#variables needed
#word in hypertext
#log(TF + 1)
#log(DF + 1 (+1 for smoothing))
#relative position of word/phrase
#whether word/phrase appears in title
#whether word/(collapsed) phrase appears in URL

#algorithm for text scanning (great for monolithic)
#* remove all undesired types of tags (e.g., <script>)
#* add a period at the end of all remaining tags to prevent run-on sentences
#* scan all words, creating sentences
#* extract monograms and bigrams from sentences

#IF doing data scan
#* do all further checks through separate find_all (or e.g., .title) function calls
#* 
#*  
#*  

def removeNonAscii(text):
	return ''.join([x for x in text if ord(x) < 128])

def append_periods_to_tags(soup,blacklist=['i','b','em','strong','small','mark','del','ins','sub','sup','a','head','html','body']):
	"""this function is used before converting html to text in order to separate elements that may not have periods after them, but should
	otherwise be separated from other bodies of text.  The blacklist skips certain tags that style text but do not interrupt sentences."""
	expr = '^((?!(' + '|'.join(blacklist) + ')).)*$'
	#print expr
	for obj in soup.find_all(re.compile(expr)):
		if obj.string <> None:
			obj.string.replace_with(obj.text + '. ')
		elif obj.strings <> None:
			last_nonempty = None
			for s in obj.strings:
				if s.findParent() is not obj:
					continue
				if s <> None:
					last_nonempty = s
				pass
			if last_nonempty <> None:
				#modified to support all languages
				last_nonempty.replace_with(last_nonempty + '. ')
	return True

def remove_unwanted(body):
	for tag in ['script','canvas']:
		res = body.find_all(tag)
		for elem in res:
			elem.decompose()
	return True

def extract_ngrams(tokens,N):
	d = dict()
	for s in tokens:
		grams = nltk.ngrams(s,N)
		for gram in grams:
			sgram = ' '.join(gram)
			d[sgram] = d.get(sgram,0)+1
	return d

def extract_monograms(tokens):
	d = dict()
	for s in tokens:
		for w in s:
			d[w] = d.get(w,0)+1
	return d

def extract_ngrams_detailed(tokens,N,other_tokens,supplied_url):
	d = dict()
	hyper_grams = extract_ngrams(other_tokens[0],N)
	title_grams = extract_ngrams(other_tokens[1],N)
	#modified to take into account no. of possible ngrams
	word_count = sum([len(x) for x in tokens]) - (N-1) * len(tokens)
	counter = 0.
	for s in tokens:
		grams = nltk.ngrams(s,N)
		for gram in grams:
			#laziness
			w = ' '.join(gram)
			is_hyperlink = 1*(w in hyper_grams)
			is_title = 1*(w in title_grams)
			#allowed for hyphen/period separation of ngrams
			in_url = 1*(re.search(re.sub(' ',r'[\-.]?',w),supplied_url) <> None)
			if w not in d:
				d[w] = {'pos':counter/max(word_count,1),'tf':1,
				'is_hyperlink':is_hyperlink,'is_title':is_title,'in_url':in_url}
			else:
				dcopy = d[w]
				dcopy['tf'] = dcopy['tf'] + 1
			counter += 1
	return d

def extract_monograms_detailed(tokens,other_tokens,supplied_url):
	d = dict()
	hyper_grams = extract_monograms(other_tokens[0])
	title_grams = extract_monograms(other_tokens[1])
	word_count = sum([len(x) for x in tokens])
	counter = 0.
	for s in tokens:
		for w in s:
			is_hyperlink = 1*(w in hyper_grams)
			is_title = 1*(w in title_grams)
			in_url = 1*(re.search(w,supplied_url) <> None)
			if w not in d:
				d[w] = {'pos':counter/max(1,word_count),'tf':1,
				'is_hyperlink':is_hyperlink,'is_title':is_title,'in_url':in_url}
			else:
				dcopy = d[w]
				dcopy['tf'] = dcopy['tf'] + 1
			counter+=1
	return d

def smart_tokenize(soup):
	"""can take either bs4 object or raw text"""
	if type(soup) == type('a'):
		raw_text = soup.lower()
	else:
		raw_text = soup.text.lower()
	sentence_tokens = nltk.sent_tokenize(raw_text)
	word_tokens = [nltk.regexp_tokenize(sentence,word_validation_regex) for sentence in sentence_tokens]
	word_tokens = [[word for word in words if word not in stopwords] for words in word_tokens]
	return word_tokens

def flatten_list(obj):
	return [x for sublist in obj for x in sublist]

def get_complete_information(filename,nvals = [1,2],supplied_url = None):
	"""gathers most necessary information about a term into a dict of dicts
	note that DF (not TF) needs to be applied separately"""
	all_tokens = extract_info(filename,False)
	broken = all_tokens[0] is []
	res = {}
	for n in nvals:
		if broken:
			res[n] = None
		if n==1:
			res[n] = extract_monograms_detailed(all_tokens[0],all_tokens[1:3],supplied_url)
		else:
			res[n] = extract_ngrams_detailed(all_tokens[0],n,all_tokens[1:3],supplied_url)
	return res

def get_tf_information(filename,nvals = [1,2]):
	body_tokens = extract_info(filename)
	res = {}
	for n in nvals:
		if n == 1:
			res[n] = extract_monograms(body_tokens)
		else:
			res[n] = extract_ngrams(body_tokens,n)
	return res


def extract_info(filename,tf_only=True):
	"""this extracts information from an html document and puts it into an 
	easily parsible format for other functions"""
	sentences = []
	with open(filename,'r') as f:
		content = f.read()
		soup = BeautifulSoup(content)
		if soup.body == None:
			print 'WARNING: ' + filename + ' has no body!'
			if not tf_only:
				return [[] , [], [] ]
			return []
		#this adds the title after the last child element of the body
		if append_title_to_body:
			new_tag = soup.new_tag('pt',string=str(soup.title))
			has_child=False
			for c in soup.body.children:
				has_child=True
			if has_child:
				c.insert_after(new_tag)
		remove_unwanted(soup.body)
		append_periods_to_tags(soup.body)
		if soup.body == None:
			print 'nooooo'
		body_tokens = smart_tokenize(soup.body)
		if not tf_only:
			#hyperlink tokens
			hyperlink_tokens = flatten_list([smart_tokenize(x) for x in soup.find_all('a') if x <> None])
			#title tokens
			if soup.title <> None:
				title_tokens = smart_tokenize(soup.title)
			else:
				title_tokens = []
			return [body_tokens,hyperlink_tokens,title_tokens]
		else:
			return body_tokens




		



def parse_document(filename):
	pass


		