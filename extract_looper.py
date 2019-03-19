import os
import datetime 
import re 
import ntpath
from difflib import get_close_matches
import nltk
import difflib
import os
import sys
import time
import ast
import numpy

from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

FULL_TEXT = 'CaseDocuments/All_FT'
EXTRACTED_CASES_FILE = 'cases.json'
EXTRACTED_SUB_KEY = 'keywords.json'

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

##
## Usage: python extract_looper.py
## Additionally: python extract_looper.py index_start index_end
##
## Goes upto, but not including index_end and starting from index_start
## 


# 1. function to get court
def ID_title_court(filename, txt):
	p, fname = os.path.split(filename)
	return [fname[0:-4], txt[0][0:-1], txt[1][0:-1]]


# 2. function to get the date
def getDate(text):

	strings = (" January "," February "," March "," April "," May "," June "," July "," August "," September "," October "," November "," December ")
	linenum = 0
	for line in text:
		linenum+=1
		if any(s in line for s in strings):
			x=0
			try:
				line = re.findall(r'[\d]+[ ]+[\w]+[ ]+[\d]+', line)[0]
				line = ' '.join(line.split())
				date_obj = datetime.datetime.strptime(line, '%d %B %Y')
				date = date_obj.date().isoformat() 
				#print(date) 
			except:
				x=1
				pass
			if (x==0):
				break
	return [date,linenum]

# 3. function to get the name of the judge
def getJudgeName(text):
	strings = ("Judgment", "delivered")
	hack = 0
	linenum = 0
	for line in text:        
		if hack == 1:
			#x = re.findall(r'[a-zA-Z][\w|.| ]+, [J][.| ]', line)
			x = re.findall(r'[a-zA-Z][\w|.| |,]+[J][.| |;|,]', line)
			if x is None:
				#print(filename,"Not Present")
				return ['Not Present', linenum]
			else:
				#print(filename,x[0])
				return [x[0], linenum]
		else:
			linenum+=1
			if all(s in line for s in strings):
			   #x = re.findall(r'((?<=by)[^\n-]+|(?<=b)[^\n-]+)', line, re.I)
				x = re.findall(r'((?<=by)[^\n-]+|(?<=b:)[^\n-]+|(?<=:)[^\n-]+)', line, re.I)
				if x is None:
					hack = 1
				else:
					x = re.findall(r'[a-zA-Z][\w|.| |\'|,]+', x[0])
					
					if len(x)==0:
						#print(filename, "Not Present")
						return ['Not Present', linenum]
					else:
						x = re.split('and', x[0])
						#print(filename,x)
						return [x,linenum]


# 4. function to get citations
def getCitations(text):
	list1=[]    
	for rd in text:
		r = re.findall(r'\S*\s\S*\s[Nn]o.\s\d{0,3}\sof\s[0-9]{4}',rd)
		s = re.findall(r'\S*\s\S*\s[Nn]o.\s\d{0,3}\sof\s[0-9]{4}-[0-9]{2}',rd)
		for r1 in r:
			if r1.find("Act")==-1 and r1.find("act")==-1:
				r1 = r1.translate({ord(c): None for c in '()[]{}'})
				text = nltk.word_tokenize(r1)
				pos=nltk.pos_tag(text)
				if not (pos[0][1]=='NN' or pos[0][1]=='NNP' or pos[0][1]=='NNS' or pos[0][1]=='NNPS'): 
					r1=r1[len(r1.split(' ',1 )[0])+1:]	
				list1.append(r1)
		for s1 in s:
			if s1.find("Act")==-1 and s1.find("act")==-1:
				s1 = s1.translate({ord(c): None for c in '()[]{}'})
				text = nltk.word_tokenize(s1)
				pos=nltk.pos_tag(text)
				if not (pos[0][1]=='NN' or pos[0][1]=='NNP' or pos[0][1]=='NNS' or pos[0][1]=='NNPS'): 
					s1=s1[len(s1.split(' ',1 )[0])+1:]	
					#print(s1,file=res)
					list1.append(s1)
	return list1

# 5. summarizer object
summarizer = LexRankSummarizer()
def summaryLooper(file):
	parser = PlaintextParser.from_file(file, Tokenizer("english"))
	summary = summarizer(parser.document, 7)
	smr = ""
	for sentence in summary:
		smr= smr + str(sentence)
	return smr


# 6. function to find the verdict
verdict_dict = {
	"allowed" : "allow",
	"disposed" : "dispose", "disposal" : "dispose", "dispose" : "dispose",
	"dismissed" : "dismiss", "dismiss" : "dismiss", "dismissal" : "dismiss",
	"order accordingly" : "accordingly", "accordingly" : "accordingly", "ordered accordingly" : "accordingly"
}
def getVerdict(txt):
	if len(txt) > 3:
		txt = txt[-3:]

	three_str = str(txt).lower()

	for item in verdict_dict:
		if item in three_str:
			return(verdict_dict[item])

	return "contention"


# 7. function to get the appeals listed in the case
def getAppeal(i,j, text):
	
	appeal=""
	for line in text[i:j-1]:
		appeal= appeal + ' ' + line
	appeal.strip()
	appeal.translate({ord('\n'): None})
	# print(appeal)
	return appeal


#function to get acts
def getActs(filename):
	f = open(filename,"r")
	tx = f.readlines()

	# Extracting lines having word " Act," in it.
	subs = " Act,"
	tx = [s for s in tx if subs in s]

	# Remove String inside the bracket
	for i in range (len(tx)):
		tx[i] = re.sub("[\(\[].*?[\)\]]","",tx[i])
		tx[i] = re.sub(' +',' ',tx[i])

	# Splitting the string
	for i in range (len(tx)):
		tx[i] = tx[i].split(' ')
		# print tx[i]

	# Find indices of occurrence of word 'Act,' 
	ind = []
	word = 'Act,'
	for i in range (len(tx)):
		if word in tx[i]:
			l=[]
			for position,name in enumerate(tx[i]):
				if name == word:
					l.append(position)
			ind.append(l)
	
	
	#print ind

	ind1 = []
	l1 = []
	for i in range (len(ind)):
		for j in range (len(ind[i])):
			c = 0
			flag = 0
			flg = 0
			while flag<2 and ind[i][j]>=c and len(tx[i])>ind[i][j]-c and len(tx[i][ind[i][j]-c])!=0:
				if tx[i][ind[i][j]-c][-1] is ',':
					flag = flag + 1
				elif tx[i][ind[i][j]-c][0].isupper() is False:
					flag = flag + 1
				elif tx[i][ind[i][j]-c][0].isupper() is True:
					flag = 0
				c = c+1
			l1.append(c)
		ind1.append(l1)
		l1=[]

	# print ind1

	txact = set()
	seperator = ' '
	for i in range (len(ind)):
		for j in range (len(ind[i])):
			if  len(tx[i])>ind[i][j]+1 and tx[i][ind[i][j]+1][0].isdigit() is True:
				tx[i][j] = seperator.join(tx[i][ind[i][j]-ind1[i][j]+3:ind[i][j]+2])

				if len(tx[i][j])>0:
					cnt = 0
					while tx[i][j][-1].isdigit() is False and cnt<10:
						tx[i][j] = tx[i][j][:-1]
						cnt = cnt+1
					if tx[i][j][0].isdigit() is False:
						txact.add(tx[i][j])
				# print (tx[i][j])
				# print(tx[i][j],file=outF)

	print(filename)
	# for res in txact:
	# print(res,file=outF)

	c = set()
	#c = []
	for res in txact:
		var = difflib.get_close_matches(res,result,n=1)
		# print(var,file=outF)
		if(len(var)>0):
			c.add(Act[var[0]])

	# print(filename,file=outF)
	print(c)


def extract_looper(index_start = 0, index_end = 53211):
	'''
		Loop over all files from 2010-2018, generate summaries and compute rouge scores
	'''

	#read all files
	files = sorted(os.listdir(FULL_TEXT))

	#create an output file to store the extracted things
	outfile = 'EXTRACTED_' + str(index_start) + '_' + str(index_end) + '.txt'

	jsonList = []

	f = open(EXTRACTED_CASES_FILE, 'r')#store your cases.json file in the same directory as this script
	extracted_acts = ast.literal_eval(f.read())
	
	f = open(EXTRACTED_SUB_KEY, 'r')
	extracted_sub_keys = ast.literal_eval(f.read())

	for index in range(index_start,index_end):

		#file = FULL_TEXT + files[index]
		file = os.path.join(FULL_TEXT,files[index])#file = os.path.join(FULL_TEXT,files[index])
		print(file)
		with open(file, 'r') as f:
			txt = f.readlines()
		
		
		idTitleCourt = ID_title_court(file, txt)
		date = getDate(txt)
		judgeName = getJudgeName(txt)
		cit = getCitations(txt)
		summary = summaryLooper(file)
		verdict = getVerdict(txt[-3:])

		if judgeName is not None:
			judge_text = judgeName[1]
		else:
			judge_text = date[1] + 2 # next line
			judgeName = [[], -1]
			# print("Not found judge~!", judgeName)
		appeal = getAppeal(date[1], judge_text,file)
		content = '\n'.join(txt[judge_text:])

		acts = []
		if idTitleCourt[0]+'.txt' in extracted_acts:
			Acts = extracted_acts[idTitleCourt[0]+'.txt']
			if acts == [""]:
				acts = []

		subject, kwords = [], ''
		if idTitleCourt[0] in extracted_sub_keys:
			subject = extracted_sub_keys[idTitleCourt[0]]['subject']
			kwords = extracted_sub_keys[idTitleCourt[0]]['keywords']

		document = {
			"num": index,
			"caseid": idTitleCourt[0],
			"title": idTitleCourt[1],
			"court": idTitleCourt[2],
			"judge": judgeName[0],
			"date": date[0],
			"citations": cit,
			"acts": acts,
			"appeal":appeal,
			"summary":summary,
			"content": content,
			"verdict" : verdict,
			"subject": subject,
			"keywords": kwords
		}
		
		# extract all fields
		print('+--- Extracting ', index-index_start, '/', index_end-index_start, ' || ', index, '/',len(files))

		jsonList.append(document)

	with open(outfile, 'w') as f:
		#f.write('[\n')
		f.write('\n'.join(str(doc) for doc in jsonList))
		f.write('\n')

	print('Done!')


if __name__ == '__main__':
	index_start, index_end = 1150, 2000
	if len(sys.argv) > 2:
		index_start, index_end = int(sys.argv[1]), int(sys.argv[2])
	extract_looper(index_start, index_end)

