import json
import re
import nltk
import sys
from nltk.stem.porter import PorterStemmer

class Stack:
	'''
	Create a stack to pop element, push element, get the peek element, determine whether the stack 
	is empty and the size of the stack. It is very helpful to deal with queries with terms and operators. 
	The principle of query searching is similar to the construction of calculator by using stack.
	'''
	def __init__(self):
		self.values = []
    
	def push(self, value):       
		self.values.append(value)

	def pop(self):
		return self.values.pop()

	def is_empty(self):
		return self.size() == 0

	def size(self):
		return len(self.values)

	def peek(self):
		return self.values[self.size()-1]


def load_json_to_dict(filename):
	'''
	Load the file index.json, and convert the data stored in json format into a dictionary containing all data.
	'''
	with open(filename) as f:
		text = f.read()
	index = json.loads(s=text)
	return index

def load_text(filename):
    with open(filename) as input_fd:
        text = input_fd.read().splitlines()
    return text

def format_result(result,num):
	'''
	Converting the computing result to the specific format. For example, '1 0 234 0 1 0'
	num is the query number and the result is the list of documents ids.
	'''
	format_list = []
	for i in result:
		string = str(num) + " 0 " + str(i) + " 0 1 0"
		format_list.append(string)
	return format_list
	
def save_result(output_file, format_list):
	'''
	Write the result into output file.
	'''
	with open(output_file, 'a') as f:
		for i in format_list:
			f.write(i+"\n")

	f.close()


def divide_stack(query_stack):
	'''
	As for query stack, divide it into two kinds of stack: operate stack and term stack.
	Terms after and before the operator are divided into two stacks for future computing.
	Distance means the distance required in the query, and the default value is 1.
	'''
	operate = Stack()
	term1 = Stack()
	term2 = Stack()
	distance = 1
	while query_stack.size() != 0:
		if query_stack.peek() == 'AND' or query_stack.peek() == 'NOT' or query_stack.peek() == 'OR':
			operate.push(query_stack.pop())
		elif '#' in query_stack.peek():
			dis = query_stack.pop()
			distance = int(dis[1:])
		elif operate.size() != 0:
			if operate.peek() == 'AND' or operate.peek() == 'OR':
				term2.push(query_stack.pop())
		else:
			term1.push(query_stack.pop())
	return operate,term1,term2,distance

def search_query(operate, term1, term2, distance, index):
	'''
	Search matched documents in different conditions.
	1. If operate stack is empty, it means that the query can be a term,
		two-term phase or two-term proximity query.
	2. if operate stack is not empty, it means that term1 stack and term2 stack 
		are not empty. In this case, we should search documents for each term stack, 
		and then do intersection or union depending on values of operators.
	'''
	result = []
	list1  = []
	list2  = []
	if operate.size() == 0: #just search a term or a phase
		result = find_term_doc(term1, distance, index)
		return result
	else: #boolean search, and operation is required
		list1 = find_term_doc(term1, distance, index)
		list2 = find_term_doc(term2, distance, index)
		if operate.size() == 1: #the operator can be 'AND' or 'OR'
			if operate.peek() == 'AND':
				for i in list1:
					for j in list2:
						if int(i) == int(j):
							if i not in result:
								result.append(i)
				return result
			elif operate.peek() == 'OR': 
				for i in list1:
					result.append(i)
				for j in list2:
					if j not in result:
						result.append(j)
				return result
		else: #the operator can be 'AND NOT'
			for i in list2:
				if i not in list1:
					if i not in result:
						result.append(i)
			return result

def find_term_doc(term, distance, index):
	'''
	Search for documents according to the term stack and the index, and then generate a list
	'''
	result = []
	if term.size() == 1:
		w = term.pop()
		result = match_doc(w,index)
		return result
	elif term.size() == 2:
		w1 = term.pop()
		w2 = term.pop()
		pos_dict1 = match_doc_pos(w1,index)
		pos_dict2 = match_doc_pos(w2,index)
		for i in pos_dict1:
				for j in pos_dict2:
					if i == j:
						pos1 = pos_dict1[i]
						pos2 = pos_dict2[j]
						for m in pos1:
							for n in pos2:
								if distance == 1:
									if n - m == 1:
										if int(i) not in result:
											result.append(int(i))
								else:
									if abs(m - n) <= distance:
										if int(i) not in result:
											result.append(int(i))
	return result

def match_doc(term,index):
	'''
	search documents for a single term according to the index, and then return the list of documents
	'''
	doc_list=[]
	for i in index:	
		if i == term:
			temp = index[i]
			for j in temp:
				doc_list.append(int(j))
	return doc_list

def match_doc_pos(term,index):
	'''
	search documents for a single term according to the index, and then return the dictionary of the positions in each documents
	'''
	doc_pos_dict = []
	for i in index:
		if i == term:
			doc_pos_dict = index[i]
	return doc_pos_dict

def analyse_query(query, stopword):
	'''
	Tokenize the query, and delete stop words, and then stem all terms, and finally push them into query stack.
	'''
	query_stack = Stack()
	token_list = tokenize_query(query)
	nostop_list = del_stopword(token_list, stopword)
	stemed_list = stem_query(nostop_list)
	for i in stemed_list:
		query_stack.push(i)
	return query_stack
	

def tokenize_query(query):
	'''
	tokenize the query, and lower the term except for operators.
	'''
	regex = re.compile(r'[\w#]+')
	temp_list = regex.findall(query)
	token_list = []
	for i in temp_list:
		if i == 'AND' or i == 'NOT' or i == 'OR':
			token_list.append(i)
		else:
			token_list.append(i.lower())
	return token_list

def stem_query(text):
	'''
	Stem all terms except for operators.
	'''
	porter=PorterStemmer()
	stemlist=[]
	for i in text:
		if i == 'AND' or i == 'NOT' or i == 'OR':
			stemlist.append(i)
		else:
			stemlist.append(porter.stem(i))
	return stemlist

def del_stopword(text,stopword):
	'''
	Delete all stop words invloved in the query.
	'''
	nostop_list = []
	for i in text:
		if i not in stopword:
			nostop_list.append(i)
	return nostop_list

def processing(query_file):
	'''
	The whole processing of Boolean Seach has been listed there.
	'''
	json_file = "index.json"
	stopword_file = "englishsw.txt"
	#query_file = "queries.boolean.txt"
	output_file = "results.boolean.txt"
	index = load_json_to_dict(json_file)
	stopword = load_text(stopword_file)
	query_list = load_text(query_file)

	for query in query_list:
		temp_query = query.split( )
		num = temp_query[0]
		temp_query.pop(0)
		real_query = (" ").join(temp_query)
		query_stack = analyse_query(real_query, stopword)
		operate,term1,term2,distance = divide_stack(query_stack)
		result = search_query(operate, term1, term2, distance, index)
		format_list = format_result(result,num)
		save_result(output_file, format_list)
		


if __name__ == '__main__':
	query_file = sys.argv[1]
	processing(query_file)
	
