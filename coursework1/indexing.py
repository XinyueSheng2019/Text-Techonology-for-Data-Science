import re
import sys
import nltk
from nltk.stem.porter import PorterStemmer
from xml.dom import minidom
from collections import defaultdict, OrderedDict
import json

def load_text(filename):
    with open(filename) as input_fd:
        text = input_fd.read().splitlines()
    return text

def preprocessing(input_file,stopword):
	'''
	Get the id, head, and text of each document, and make lists for document id, and the combination of headline and text.
	'''
	word = ""
	id1 = 0
	num_terms_dict={}
	term_dict = defaultdict(dict)
	porter=PorterStemmer()

	with open(input_file,'r',encoding='utf8') as f:
		regex = re.compile(r"[\w']+")
		dom = minidom.parse(f) #load xml file
		doc_num = dom.getElementsByTagName("DOCNO")	
		doc_head = dom.getElementsByTagName("HEADLINE")
		doc_text = dom.getElementsByTagName("TEXT")
		n = 0
		for i in range(len(doc_num)):  
			text = doc_head[i].firstChild.data + doc_text[i].firstChild.data
			m = 1
			term_list = []
			pos_terms_dict = {}
			words = regex.findall(text)	#tokenise text
			for word in words:
				word = word.replace("\"",'').replace("\'s",'').replace("\'",'')
				if word != '':
					word = word.lower()#lower every term
					if word not in stopword: #drop stop words
						word = porter.stem(word)#stem the term
						if word not in term_dict:
							term_dict.setdefault(word,dict())
						if doc_num[i].firstChild.data not in term_dict[word]:
							term_dict[word].setdefault(doc_num[i].firstChild.data,list())

						term_dict[word][doc_num[i].firstChild.data].append(m) #construct inverted index
						m += 1					
			n += 1
		dict_list = sorted(term_dict.items(),key=lambda x:x[0])
		return term_dict,dict_list

def save_result_txt(output_file, dict_list):

	with open(output_file, 'w') as f:
		for i in range(len(dict_list)):
			f.write(str(dict_list[i][0])+":("+str(len(dict_list[i][1]))+")\n")
			for j in dict_list[i][1]:
				termstring=",".join('%s' %id for id in dict_list[i][1][j])
				f.write("	" + str(j) + ":(" + str(len(dict_list[i][1][j])) + ") " + termstring + "\n")
	f.close()

def save_result_json(output_file, term_dict):
	json_str = json.dumps(term_dict, indent = 4)
	with open(output_file, 'w') as f:
		f.write(json_str)
	f.close()


def indexing(input_file):
	'''
	The whole processing of indexing has been listed there.

	'''
	print("Programming starts.")
	stopword_file = "englishsw.txt"
	output_file_txt = "index.txt"
	output_file_json = "index.json"
	stopword = load_text(stopword_file)
	term_dict,dict_list = preprocessing(input_file,stopword)
	print("Save the result.")
	save_result_txt(output_file_txt, dict_list)
	save_result_json(output_file_json, term_dict)
	print("Programming finished!")

if __name__ == '__main__':
	input_file = sys.argv[1]
	indexing(input_file)



