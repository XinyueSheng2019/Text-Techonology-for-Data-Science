import json
import re
import nltk
import sys
import math
from decimal import Decimal
from xml.dom import minidom
from nltk.stem.porter import PorterStemmer

def load_xml_file(input_file):
	'''
	Get the number of  document from original xml file
	'''
	doc_num = []
	with open(input_file,'r',encoding='utf8') as f:
		dom = minidom.parse(f) #load xml file
		doc_num = dom.getElementsByTagName("DOCNO")
	return len(doc_num)

def load_json_to_dict(filename):
	'''
	Load the file index.json, and convert the data stored in json format into a dictionary containing all data.
	'''
	with open(filename) as f:
		text = f.read()
	index = json.loads(s=text)
	return index

def load_text(filename):
	"""
    Load lines from a plain-text file and return these as a list, with
    trailing newlines stripped.
    """
	with open(filename,'r') as f:
		lines = f.read().splitlines()
	return lines

def save_file(output_file, result_list):
	with open(output_file, 'a') as f:
		if len(result_list) > 1000:
			n = 0
			while n <= 999:
				f.write(result_list[n] + "\n")
				n = n + 1
		else:
			n = 0
			while n < len(result_list):
				f.write(result_list[n] + "\n")
				n = n + 1
	f.close()


def tfidf_processing(termlist, index, N):
	'''
	Calculate tfidf
	tf means tf(t,d)
	df means df(t)
	w means weight
	'''
	doc_list = search_docoments(termlist,index)
	score_dict = {}
	for d in doc_list:
		n = 1
		score = 0
		while n < len(termlist):
			df = calculate_df(termlist[n],index)
			if d in [i for i in index[termlist[n]]]:
				tf = calculate_tf(termlist[n], d, index)
				w  = calculate_weight(tf, df, N)
			else:
				w = 0
			score = score + w
			n = n + 1
		# keep 4 decimal places
		a = Decimal(score)	
		score_dict[d] = round(a,4)

	return score_dict

		
def sort_score(score_dict):
	return sorted(score_dict.items(), key=lambda x:x[1], reverse=True)
	
def format_result(sort_result, termlist):
	result_list = []
	for i in sort_result:
		str_result = termlist[0] + " 0 "+ i[0]+ " 0 " + str(i[1]) + " 0"
		result_list.append(str_result)
	return result_list

def search_docoments(termlist, index):
	"""
	find every docoment that includes the terms in the query
	"""
	doc_list = []
	size = len(termlist)	
	doc_list = [i for i in index[termlist[1]]]
	n = 1
	while n < len(termlist)-1:
		for d in [i for i in index[termlist[n+1]]]:
			if d not in doc_list:
				doc_list.append(d)
		n = n + 1
	return doc_list
		

def calculate_tf(term, d, index): 
	return len(index[term][d])

def calculate_df(term, index):
	return len(index[term])

def calculate_weight(tf, df, N):
	return (1 + math.log(tf,10))*math.log(N/df,10)

def analyse_query(query, stopword):

	token_list = tokenize_query(query)
	nostop_list = del_stopword(token_list, stopword)
	stemed_list = stem_query(nostop_list)
	return stemed_list
	

def tokenize_query(query):
	regex = re.compile(r'[\w#]+')
	temp_list = regex.findall(query)
	token_list = []
	for i in temp_list:
		token_list.append(i.lower())
	return token_list

def stem_query(text):
	porter=PorterStemmer()
	stemlist=[]
	for i in text:
		stemlist.append(porter.stem(i))
	return stemlist

def del_stopword(text,stopword):
	nostop_list = []
	for i in text:
		if i not in stopword:
			nostop_list.append(i)
	return nostop_list


def processing(json_file, query_file, stopword_file, output_file, N):
	'''
	The whole processing of calculating tfidf and storing the result has been listed there.
	'''
	index = load_json_to_dict(json_file)
	stopword = load_text(stopword_file)
	query_list = load_text(query_file)
	for query in query_list:
		termlist    = analyse_query(query, stopword)
		score_dict  = tfidf_processing(termlist, index, N)
		sort_result = sort_score(score_dict)
		result_list = format_result(sort_result,termlist)
		save_file(output_file, result_list)



if __name__ == '__main__':
	json_file = "index.json"
	query_file = sys.argv[1]
	stopword_file = "englishsw.txt"
	xml_file='trec.5000.xml'
	output_file = 'results.ranked.txt'
	N = load_xml_file(xml_file)
	print("programming starts...")
	processing(json_file, query_file, stopword_file, output_file, N)




