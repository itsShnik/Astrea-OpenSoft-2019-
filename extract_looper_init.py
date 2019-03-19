import os
import nltk
import sys
import time


FULL_TEXT = 'CaseDocuments/All_FT/'

##
## Usage: python extract_looper.py
## Additionally: python extract_looper.py index_start index_end
##
## Goes upto, but not including index_end and starting from index_start
## 


def extract_looper(index_start = 0, index_end = 53211):
	'''
		Loop over all files from 2010-2018, generate summaries and compute rouge scores
	'''
	
	files = sorted(os.listdir(FULL_TEXT))
	outfile = 'EXTRACTED_' + str(index_start) + '_' + str(index_end) + '.txt'
	jsonList = []

	for index in range(index_start, index_end):
		file = FULL_TEXT + files[index]
		document = {'name': index}

		# extract all fields
		print('+--- Extracting ', index-index_start, '/', index_end-index_start, ' || ', index, '/',len(files))

		jsonList.append(document)

	with open(outfile, 'w') as f:
		f.write('[\n')
		f.write(',\n'.join(['  ' + str(doc) for doc in jsonList]))
		f.write('\n]\n')

	print('Done!')


if __name__ == '__main__':
	index_start, index_end = 0, 53211
	if len(sys.argv) > 2:
		index_start, index_end = int(sys.argv[1]), int(sys.argv[2])
	extract_looper(index_start, index_end)