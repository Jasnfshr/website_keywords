import random
import os
import sys
import shutil


def main():
	os.chdir('webpages')
	print os.getcwd()
	files = os.listdir(os.getcwd())
	selected = random.sample(files,15)
	for filename in selected:
		print filename
		shutil.copy(filename,'../clustering_training/' + filename)
		f = open('../clustering_training/' + filename + '.key','a')
		f.close()

if __name__ == '__main__':
	main()