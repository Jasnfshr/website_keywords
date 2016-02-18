import random
import os
import sys
import shutil


def main(args):
	os.chdir('webpages')
	print os.getcwd()
	if len(args) > 0:
		try:
			nsamples = int(args[0])
		except:
			nsamples = 20
	else:
		nsamples = 20
	files = os.listdir(os.getcwd())
	selected = random.sample(files,nsamples)
	for filename in selected:
		print filename
		shutil.copy(filename,'../clustering_training/' + filename)
		f = open('../clustering_training/' + filename + '.key','a')
		f.close()

if __name__ == '__main__':
	main(sys.argv[1:])