import os
import sys
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer 
from nltk.tokenize import word_tokenize
from spellchecker import SpellChecker
import datetime
import re

stop_words = set(stopwords.words('english'))

dict = {
			"allowed" : "Appeal Allowed",
			"disposed" : "Petition Disposed",
			"disposal" : "Petition Disposed",
			"dispose" : "Petition Disposed",
			"dismissed" : "Petition Dismissed",
			"dismiss" : "Petition Dismissed",
			"order accordingly" : "Order Accordingly",
			"accordingly" : "Order Accordingly",
			"ordered accordingly" : "Order Accordingly"
		}

verdict_tokens = []
legal_tokens = []
judge_name_tokens = []
other_tokens = []

class PreProcessing:
	def __init__(self):
		pass

	def filtered_word_tokens(self, query):
		#pass the query string
		word_tokens = word_tokenize(query.replace(',','').replace('.', '').strip().lower())
		#print(word_tokens)
		filtered_word_tokens = []
		for word in word_tokens:
			if word not in stop_words:
				filtered_word_tokens.append(word)
		return filtered_word_tokens

	def corrected_word_tokens(self, tokens):
		spell = SpellChecker()
		spell.distance = 1
		corrected_word_tokens = []
		for token in tokens:
			corrected_word_tokens.append(spell.correction(token))
		return corrected_word_tokens

	def pos_tagged_tokens(self, tokens):
		#pass filtered tokens
		pos_tagged = nltk.pos_tag(tokens)

		wordnet_pos_tagged = []
		for i in pos_tagged:
			#print(i)
			if i[1].startswith('J'):
				tupl = (i[0], wordnet.ADJ)
			elif i[1].startswith('V'):
				tupl =  (i[0], wordnet.VERB)
			elif i[1].startswith('N'):
				tupl = (i[0], wordnet.NOUN)
			elif i[1].startswith('R'):
				tupl = (i[0], wordnet.ADV)
			else:
				tupl = (i[0], wordnet.NOUN)
			wordnet_pos_tagged.append(tupl)

		return pos_tagged, wordnet_pos_tagged #return a list of 2 element tuples

	def noun_tokens(self, tokens):
		#pass the pos_tagged tokens
		noun_tokens = []
		for i in tokens:
			if i[1].startswith('N'):
				noun_tokens.append(i[0])
		return noun_tokens

	def lemmatized_tokens(self, tokens):
		#pass the wordnet_tagged tokens
		lemmatized_tokens = []
		ltz = WordNetLemmatizer()
		for token in tokens:
			word = ltz.lemmatize(token[0], token[1])
			lemmatized_tokens.append(word)

		return lemmatized_tokens

class QueryParser:
	def __init__(self):
		pass

	def find_date_duration(self, query):
		ranges = []
		fromTo = re.findall(r'[Ff][Rr][Oo][Mm]\s[0-9]{1,}\s[Tt][Oo]\s[0-9]{1,}',query)
		for fromToSubStrings in fromTo:
			temp = re.findall(r'[0-9]{1,}',fromToSubStrings)
			# create tupple only if dates in right order
			if int(temp[0]) < int(temp[1]):
				tupleTemp = (temp[0], temp[1])
			ranges.append(tupleTemp)

		beforeAfterSubStringsYears = []
		

		beforeAfter = re.findall(r'[Bb][Ee][Ff][Oo][Rr][Ee]\s[0-9]{1,}\s[Aa][Ff][Tt][Ee][Rr]\s[0-9]{1,}',query)
		for beforeAfterSubStrings in beforeAfter:
			temp = re.findall(r'[0-9]{1,}',beforeAfterSubStrings)
			beforeAfterSubStringsYears.append(temp[0])
			beforeAfterSubStringsYears.append(temp[1])
			# create tupple only if dates in right order
			if int(temp[1]) < int(temp[0]):
				tupleTemp = (temp[1], temp[0])
			else: 
				tupleTemp = (temp[0], temp[1])
			ranges.append(tupleTemp)

		beforeTAfter = re.findall(r'[Bb][Ee][Ff][Oo][Rr][Ee]\s[0-9]{1,}\s\b[a-zA-Z0-9_]+\b\s[Aa][Ff][Tt][Ee][Rr]\s[0-9]{1,}',query)
		for beforeAfterSubStrings in beforeTAfter:
			temp = re.findall(r'[0-9]{1,}',beforeAfterSubStrings)
			beforeAfterSubStringsYears.append(temp[0])
			beforeAfterSubStringsYears.append(temp[1])
			# create tupple only if dates in right order
			if int(temp[1]) < int(temp[0]):
				tupleTemp = (temp[1], temp[0])
			else: 
				tupleTemp = (temp[0], temp[1])
			ranges.append(tupleTemp)
		
		lll = re.findall(r'[0-9]{1,}\s[Yy][Rr]\s[Bb][Ee][Ff][Oo][Rr][Ee]\s[0-9]{1,}',query)
		for lastYearsSubStrings in lll:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStrings)
			beforeAfterSubStringsYears.append(str(int(temp[1])-int(temp[0])))
			beforeAfterSubStringsYears.append(temp[1])
			tupleTemp = ( str(int(temp[1])-int(temp[0])), str(int(temp[1])))
			ranges.append(tupleTemp)

		llll = re.findall(r'[0-9]{1,}\s[Yy][Rr][Ss]\s[Bb][Ee][Ff][Oo][Rr][Ee]\s[0-9]{1,}',query)
		for lastYearsSubStrings in lll:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStrings)
			beforeAfterSubStringsYears.append(str(int(temp[1])-int(temp[0])))
			beforeAfterSubStringsYears.append(temp[1])
			tupleTemp = ( str(int(temp[1])-int(temp[0])), str(int(temp[1])))
			ranges.append(tupleTemp)

		lrl = re.findall(r'[0-9]{1,}\s[Yy][Ee][Aa][Rr]\s[Bb][Ee][Ff][Oo][Rr][Ee]\s[0-9]{1,}',query)
		for lastYearsSubStringss in lrl:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStringss)
			beforeAfterSubStringsYears.append(str(int(temp[1])-int(temp[0])))
			beforeAfterSubStringsYears.append(temp[1])
			tupleTemp = ( str(int(temp[1])-int(temp[0])), str(int(temp[1])))
			ranges.append(tupleTemp)

		lrlf = re.findall(r'[0-9]{1,}\s[Yy][Ee][Aa][Rr][Ss]\s[Bb][Ee][Ff][Oo][Rr][Ee]\s[0-9]{1,}',query)
		for lastYearsSubStringss in lrlf:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStringss)
			beforeAfterSubStringsYears.append(str(int(temp[1])-int(temp[0])))
			beforeAfterSubStringsYears.append(temp[1])
			tupleTemp = ( str(int(temp[1])-int(temp[0])), str(int(temp[1])))
			ranges.append(tupleTemp)

		rrrr = re.findall(r'[0-9]{1,}\s[Yy][Rr][Ss]\s[Aa][Ff][Tt][Ee][Rr]\s[0-9]{1,}',query)
		for lastYearsSubStrings in rrrr:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStrings)
			beforeAfterSubStringsYears.append(str(int(temp[1])+int(temp[0])))
			beforeAfterSubStringsYears.append(temp[1])
			tupleTemp = (str(int(temp[1])), str(int(temp[0])+int(temp[1])))
			ranges.append(tupleTemp)

		rrr = re.findall(r'[0-9]{1,}\s[Yy][Rr]\s[Aa][Ff][Tt][Ee][Rr]\s[0-9]{1,}',query)
		for lastYearsSubStrings in rrr:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStrings)
			beforeAfterSubStringsYears.append(str(int(temp[1])+int(temp[0])))
			beforeAfterSubStringsYears.append(temp[1])
			tupleTemp = (str(int(temp[1])), str(int(temp[0])+int(temp[1])))
			ranges.append(tupleTemp)

		rrll = re.findall(r'[0-9]{1,}\s[Yy][Ee][Aa][Rr][Ss]\s[Aa][Ff][Tt][Ee][Rr]\s[0-9]{1,}',query)
		for lastYearsSubStrings in rrll:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStrings)
			beforeAfterSubStringsYears.append(str(int(temp[1])+int(temp[0])))
			beforeAfterSubStringsYears.append(temp[1])
			tupleTemp = (str(int(temp[1])), str(int(temp[0])+int(temp[1])))
			ranges.append(tupleTemp)

		rlrl = re.findall(r'[0-9]{1,}\s[Yy][Ee][Aa][Rr]\s[Aa][Ff][Tt][Ee][Rr]\s[0-9]{1,}',query)
		for lastYearsSubStrings in rlrl:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStrings)
			beforeAfterSubStringsYears.append(str(int(temp[1])+int(temp[0])))
			beforeAfterSubStringsYears.append(temp[1])
			tupleTemp = (str(int(temp[1])), str(int(temp[0])+int(temp[1])))
			ranges.append(tupleTemp)

		before = re.findall(r'[Bb][Ee][Ff][Oo][Rr][Ee]\s[0-9]{4}',query)
		for beforeSubStrings in before:
			temp = re.findall(r'[0-9]{4}',beforeSubStrings)
			for tempWord in temp:
				print(tempWord)
				if tempWord not in beforeAfterSubStringsYears:
					ranges.append( ('1953',tempWord) )
		
		after = re.findall(r'[Aa][Ff][Tt][Ee][Rr]\s[0-9]{4}',query)
		for afterSubStrings in after:
			temp = re.findall(r'[0-9]{4}',afterSubStrings)
			for tempWord in temp:
				print(tempWord)
				if tempWord not in beforeAfterSubStringsYears:
					ranges.append( (tempWord , '2019') )
		
		lastYears = re.findall(r'[Ll][Aa][Ss][Tt]\s[0-9]{1,}\s[Yy][Ee][Aa][RrSs]',query)
		for lastYearsSubStrings in lastYears:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStrings)
			tupleTemp = ( str(2019-int(temp[0])), '2019')
			ranges.append(tupleTemp)

		lastYrs = re.findall(r'[Ll][Aa][Ss][Tt]\s[0-9]{1,}\s[Yy][RrSs]',query)
		for lastYearsSubStrings in lastYrs:
			temp = re.findall(r'[0-9]{1,}',lastYearsSubStrings)
			tupleTemp = ( str(2019-int(temp[0])), '2019')
			ranges.append(tupleTemp)

		date_tokens = []
		for i in ranges:
			date_tokens.append(i[0])
			date_tokens.append(i[1])

		return ranges, date_tokens


	def find_verdict_tokens(self, tokens):
		ver_tokens = []
		for word in tokens:
			if word in dict:
				ver_tokens.append(dict[word])
		return ver_tokens

	def find_legal_tokens(self, tokens):
		legal_tokens = []
		with open("Law_Vocabulary.txt", "r") as f:
			text = f.readlines()
		for token in tokens:
			try:
				numeral = int(token)
				continue
			except:
				for i in range(len(text)):
					if token in text[i].lower().split():
						legal_tokens.append(token)
						break

		return legal_tokens

	def find_judge_names(self, tokens):
		with open("judgesnames.txt", "r") as f:
			text = f.readlines()
		jn_tokens = []
		for token in tokens:
			for i in range(len(text)):
				if token in text[i].replace(',','').replace('.', '').strip().lower()\
					and token not in jn_tokens:
					jn_tokens.append(token)
		return jn_tokens

def parse_query(querystr):
	pp = PreProcessing()
	filtered_word_tokens = pp.filtered_word_tokens(querystr)
	corrected_word_tokens = pp.corrected_word_tokens(filtered_word_tokens)
	pos_tagged_tokens, wordnet_pos_tagged_tokens = pp.pos_tagged_tokens(corrected_word_tokens)
	lemmatized_tokens = pp.lemmatized_tokens(wordnet_pos_tagged_tokens)
	noun_tokens = pp.noun_tokens(pos_tagged_tokens)

	parser = QueryParser()
	duration, date_tokens = parser.find_date_duration(querystr)
	verdict_tokens = parser.find_verdict_tokens(corrected_word_tokens)
	legal_tokens = parser.find_legal_tokens(lemmatized_tokens)
	judge_name_tokens = parser.find_judge_names(noun_tokens)
	other_tokens = []
	for token in corrected_word_tokens:
		if token not in verdict_tokens and token not in judge_name_tokens\
			 and token not in legal_tokens and token not in date_tokens:
			other_tokens.append(token)

	return duration, verdict_tokens, legal_tokens, judge_name_tokens, other_tokens


if __name__ == '__main__':
	querystr = ""
	querystr = sys.argv[1]
	duration, verdict_tokens, legal_tokens, judge_name_tokens, other_tokens = \
		parse_query(querystr)
	print("duration :::", duration)
	print("\n")
	print("verdict ::: ", verdict_tokens)
	print("\n")
	print("legal tokens ::: ", legal_tokens)
	print("\n")
	print("judge tokens :::", judge_name_tokens)
	print("\n")
	print("other tokens ::: ", other_tokens)

"""
querystr = sys.argv[1]
parser = QueryParser()
#date_tokens = parser.find_date(querystr)#list of 2 element tuples
filtered_word_tokens = parser.word_tokens(querystr)
verdict_tokens = parser.find_verdict(filtered_word_tokens)
pos_tagged = parser.pos_tagger(filtered_word_tokens)
print(filtered_word_tokens)
print(verdict_tokens)
print(pos_tagged)
noun_tokens = []
for i in pos_tagged:
	if pos_tagged is not None and i[1] == 'NN':
		noun_tokens.append(i[0])

print(noun_tokens)
judge_name_tokens = parser.find_judge_names(noun_tokens)
legal_tokens = parser.find_legal_tokens(filtered_word_tokens)
other_tokens = parser.find_other_tokens(filtered_word_tokens)
print(judge_name_tokens)
print(other_tokens)



#remove stopwords to get filtered_tokens
#find verdict tokens
"""