import sys
import re
import math

def load_file(input_file):
	with open(input_file) as f:
		text = f.read().splitlines()
	return text

def calculate_DCG(doc_list_num,query_related_dict,k):
	n = 1
	if doc_list_num[0] in query_related_dict:
		rel1 = int(query_related_dict[doc_list_num[0]])
	else: 
		rel1 = 0
	DCG = rel1 #the first document rank1 rel1
	n = n + 1

	while(n != (k+1)): #for document ranked k, calculate the DG
		if doc_list_num[n-1] in query_related_dict:
			DG = int(query_related_dict[doc_list_num[n-1]])/math.log(n,2)
		else:
			DG = 0
		DCG += DG
		n = n + 1

	return DCG

def sort_dict_by_grade(query_related_dict,k):
	if len(query_related_dict)>=k:
		return [d[0] for d in sorted(query_related_dict.items(),key=lambda x:x[1],reverse=True)[:k]]
	else:
		ori = [d[0] for d in sorted(query_related_dict.items(),key=lambda x:x[1],reverse=True)]
		l = len(ori)
		while (l!=k+1):
			ori.append('null')
			l = l + 1
		return ori


def mean_value(value_list):
 #get the average value of all elements in a list
	sum_value = 0
	n = 0
	while(n<len(value_list)):
		sum_value += float(value_list[n])
		n = n + 1
	return '%.3f' % (sum_value/len(value_list))



if __name__=='__main__':
	related_file = 'systems/qrels.txt'
	related_list = load_file(related_file)
	regex = re.compile(r"[\w]+")
	with open("All.eval","w") as a:
		a.write("\tP@10\tR@50\tr-Precision\tAP\tnDCG@10\tnDCG@20\n")

		for i in range(1,7): #open each system file
			print("this is system "+ str(i))
			input_file = 'systems/S'+str(i)+'.results'
			rank_list = load_file(input_file)
			P = [] #precision list
			R = [] #recall list
			r_precision = []
			AP = []
			nDCG10_query = []
			nDCG20_query = []

			for n in range(1,11): 
				#doc_list_K is the top k retrieval documents for each query in each system
				doc_list_10 = [d.split()[2] for d in [x for x in rank_list if int(x[:2])==n][:10]]
				doc_list_20 = [d.split()[2] for d in [x for x in rank_list if int(x[:2])==n][:20]]
				doc_list_50 = [d.split()[2] for d in [x for x in rank_list if int(x[:2])==n][:50]]
				
				#query_list is the related documents for each query
				query_list = regex.findall(related_list[n-1]) 
				
				t = 1
				#query_related_dict is a dictionary containing the relevant document and its grade
				query_related_dict = {} 
				
				while(t != len(query_list)):
					query_related_dict[query_list[t]] = query_list[t+1] 
					t = t + 2

				#tpK_list is a list containing the documents which is included in the top K retrieval documents and relevant documents.
				tp10_list = [d for d in doc_list_10 if d in query_related_dict]
				tp50_list = [d for d in doc_list_50 if d in query_related_dict]
 
				#calculate P@10
				P.append('%.3f' % (len(tp10_list)/10.0))

				#calculate R@50
				R.append('%.3f' % (len(tp50_list)*1.0/len(query_related_dict)))

				#calculate P@r
				doc_list_r = [d.split()[2] for d in [x for x in rank_list if int(x[:2])==n][:len(query_related_dict)]]
				pr_list = [d for d in doc_list_r if d in query_related_dict]
				r_precision.append('%.3f' % (len(pr_list)/len(doc_list_r)))
				
				#MAP
				doc_list_all = [d.split()[2] for d in [x for x in rank_list if int(x[:2])==n]]
				sum_AP = 0
				for d in doc_list_all:
					if d in query_related_dict:
						pos = doc_list_all.index(d)+1
						sum_AP += len([m for m in doc_list_all[:pos] if m in query_related_dict])/pos
				if sum_AP != 0:
					AP.append('%.3f' % (sum_AP/len(query_related_dict)))
				else:
					AP.append('%.3f' % 0)
				
				#DCG@10
				DCG10 = calculate_DCG(doc_list_10,query_related_dict,10)	

				#iDCG@10
				sort_relavent_10_list = sort_dict_by_grade(query_related_dict,10)
				iDCG10 = calculate_DCG(sort_relavent_10_list,query_related_dict,10)

				#nDCG@10
				if iDCG10 == 0:
					nDCG10_query.append('%.3f' % 0)
				else:
					nDCG10_query.append('%.3f' % (DCG10/iDCG10))

				#DCG@20
				DCG20 = calculate_DCG(doc_list_20,query_related_dict,20)

				#iDCG@20
				sort_relavent_20_list = sort_dict_by_grade(query_related_dict,20)
				iDCG20 = calculate_DCG(sort_relavent_20_list,query_related_dict,20)

				#nDCG@20
				if iDCG20 == 0:
					nDCG20_query.append('%.3f' % 0)
				else:
					nDCG20_query.append('%.3f' % (DCG20/iDCG20))

			output_file = "S"+str(i)+".eval"
			with open(output_file,"w") as f:
				f.write("\tP@10\tR@50\tr-Precision\tAP\tnDCG@10\tnDCG@20\n")
				for q in range(1,11):
					f.write(str(q)+"\t"+P[q-1]+"\t"+R[q-1]+"\t"+r_precision[q-1]+"\t"+AP[q-1]+"\t"+nDCG10_query[q-1]+"\t"+nDCG20_query[q-1]+"\n")
				
				f.write("mean\t"+mean_value(P)+"\t"+mean_value(R)+"\t"+mean_value(r_precision)+"\t"+mean_value(AP)+"\t"+mean_value(nDCG10_query)+"\t"+mean_value(nDCG20_query)+"\n")
				a.write("S"+str(i)+"\t"+mean_value(P)+"\t"+mean_value(R)+"\t"+mean_value(r_precision)+"\t"+mean_value(AP)+"\t"+mean_value(nDCG10_query)+"\t"+mean_value(nDCG20_query)+"\n")

			f.close()
	a.close()
			

			

