import random
import os
import sys
import shutil


def main():
	os.chdir('webpages')
	print os.getcwd()
	files = os.listdir(os.getcwd())
	selected = random.sample(files,100)
	for filename in selected:
		print filename
		shutil.copy(filename,'../keyword_training/' + filename)
		f = open('../keyword_training/' + filename + '.key','a')
		f.close()

if __name__ == '__main__':
	main()