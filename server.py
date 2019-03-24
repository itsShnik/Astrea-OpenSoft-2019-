from flask import Flask,request
from elasticsearch_dsl import Search,Q
from elasticsearch import Elasticsearch
import json
import gensim.models as g
import codecs
import numpy as np
import numpy.linalg as LA
import functools
from subprocess import *


ES_HOST   = {"host":"localhost","port":9200}
client = Elasticsearch(hosts=[ES_HOST])
query_ = []

app = Flask(__name__)

@app.route("/")
def welcome():
    return ("Server Started")

@app.route("/search")
def compare(item1, item2):
	cosine_function = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3)
    cosine1 = cosine_function(item1['vector'], query_)
    cosine2 = cosine_function(item2['vector'], query_)
	return cosine2-cosine1

def search():
    query=request.args.get('q')
    judge=request.args.get('judge')
    category=request.args.get('category')
    acts=request.args.get('acts')
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    verdict_tokens = []
    legal_tokens = []
    judge_name_tokens = []
    other_tokens = []
    duration, verdict_tokens, legal_tokens, judge_name_tokens, other_tokens = parse_query(query)
    print("duration :::", duration)
	print("\n")
	print("verdict ::: ", verdict_tokens)
	print("\n")
	print("legal tokens ::: ", legal_tokens)
	print("\n")
	print("judge tokens :::", judge_name_tokens)
	print("\n")
	print("other tokens ::: ", other_tokens)

	string legal_other;
	for i in legal_tokens+other_tokens:
		legal_other+=" "+i;
	for i in judge_name_tokens:
		judge+=" "+i;
	string verdict;
	for i in verdict_tokens:
		verdict+=" "+i;

    file_object = open('things.txt', "w+")
    file_object1 = open('Word2.txt', "w+")

    for i in range(0, len(legal_other)):
    	t = query[i]
    	t = t + '\n'
    	file_object.write(t)
    print(q)
    call(["./distance" , "vectors.bin"],  stdin = file_object, stdout = file_object1)

    t = file_object1.readLines()
    t1 = t[0]
    queryNew = ''
    for i in range(0, len(t1)-2):
    	queryNew = queryNew + t1[i]

    print(queryNew)

    s = Search(using=client)
    should =[]
    if(query is not None):
        q_base=Q('multi_match',query=queryNew,fuzziness="1",prefix_length=3)
        should.append(q_base)
    if(judge is not None):
        q_judge = Q('multi_match',query=judge,fields=['judge'])
        should.append(q_judge)
    if(acts is not None):
        q_acts = Q('multi_match',query=acts,fields=['acts'])
        should.append(q_acts)
    if(category is not None):
        q_category = Q('multi_match',query=category,fields=['subject'])
        should.append(q_category)
    if(date_from is not None and date_to is not None):
        q_date = Q('range',fields=['date'],gte=date_from,lte=date_to,format="yyyy/MM/dd")
        should.append(q_date)
    if(date_from is None and date_to is not None):
        q_date = Q('range',fields=['date'],gte="1940/01/01",lte=date_to,format="yyyy/MM/dd")
        should.append(q_date)
    if(date_from is not None and date_to is not None):
        q_date = Q('range',fields=['date'],gte=date_from,lte="now",format="yyyy/MM/dd")
        should.append(q_date)
    q = Q('bool',should=should,minimum_should_match=len(should))
    s=s.query(q)
    count=s.count()
    response = s[0:count].execute()
    response= response.to_dict()
    result={}

    model="doc2vec.bin"
    start_alpha=0.01
    infer_epoch=1000
    m = g.Doc2Vec.load(model)
    query_ = query
    query_ = query_.strip().split()
    query_ = m.infer_vector(query_, alpha=start_alpha, steps=infer_epoch)
    for i in range(len(response['hits']['hits'])):
    	resp = response['hits']['hits'][i]["_source"]
    	resp['score']=response['hits']['hits'][i]["_score"]
    	result[str(i)]=resp

    result_ = result.values()
	result_ = sorted(result_, key=functools.cmp_to_key(compare))
	result = {}
	for i in range(len(response['hits']['hits'])):
    	result[str(i)]=result_[i]

    return json.dumps(result)
