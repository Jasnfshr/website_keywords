import os
import re

print 'removing training samples with no keywords...'

BASE_DIRECTORY = '/home/max/workspace/webclass/keyword_training/'

os.chdir(BASE_DIRECTORY)
files = [f for f in os.listdir(os.getcwd()) if re.match('.*html$',f) <> None]
keyfiles = [f + '.key' for f in files]

for keyfile, fn in zip(keyfiles,files):
	size = os.stat(keyfile).st_size
	if size < 8:
		print 'removing: ' + keyfile
		print 'removing: ' + fn
		os.remove(keyfile)
		os.remove(fn)

print 'done'