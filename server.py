from flask import Flask,request
from elasticsearch_dsl import Search,Q
from elasticsearch import Elasticsearch
import json
import codecs
import numpy as np
import numpy.linalg as LA
import functools
from finalQueryParser import parse_query
from subprocess import *
import re
import os
import subprocess

# ES_HOST   = {"host":"206.189.138.208","port":9200}
ES_HOST   = {"host":"127.0.0.1","port":9200}
# client1 = Elasticsearch(hosts=[ES_HOST],index="test")
# client2 = Elasticsearch(hosts=[ES_HOST],index="index")
client = Elasticsearch(hosts=[ES_HOST])
query_ = []

app = Flask(__name__)
## CORS
from flask_cors import CORS, cross_origin
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def welcome():
    return ("Server Started")

def compare(item1, item2):
    cosine_function = lambda a, b : round(np.inner(np.array(a), np.array(b))/(LA.norm(a)*LA.norm(b)), 3)
    cosine1 = cosine_function(item1['vector'], query_)
    cosine2 = cosine_function(item2['vector'], query_)
    return cosine2-cosine1

@app.route("/search")
def search():
    query=request.args.get('q')
    judge=request.args.get('judge')
    category=request.args.get('category')
    acts=request.args.get('acts')
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    start = request.args.get('pagenum')
    if start:
        start = int(start) * 20
    else:
        start = 0
    verdict_tokens = []
    legal_tokens = []
    judge_name_tokens = []
    other_tokens = []
    judge2=""

    if query is not None:
     
        duration, verdict_tokens, legal_tokens, judge_name_tokens, other_tokens = parse_query(query)
        legal_other = legal_tokens + other_tokens
        verdict = ""
        for i in judge_name_tokens:
            if i is not None:
                judge2+=" "+i

        for i in verdict_tokens:
            if i is not None:
                verdict+=" "+i

        print(legal_other)

        file_object = open('things.txt', "w+")
        # file_object1 = open('Word2.txt', "w+")

        for i in range(0,len(legal_other)):
            t = legal_other[i]
            t = t + '\n'
            print(t)
            file_object.write(t)

        t='EXIT'
        t = t + '\n'
        file_object.write(t)    
        file_object.close()
        # file_object11 = open('things.txt', "r")
        subprocess.Popen("./distance vectors.bin < things.txt > Word2.txt", shell=True)
        # call("["./distance" , "vectors.bin"],  stdin = file_object11, stdout = file_object1)

        # file_object1.close()

        with open('Word2.txt', 'r') as f:
            strin = f.read()

        words = re.sub('[^a-zA-Z0-9\n]', ',', strin)
        words = list([x for x in set(words.split(',')) if x!=query])
        print(words)
        new_str = query + ' ' + ' '.join(words [ : min(10,len(words))] )
        

        # with open('Word2.txt', 'r') as f:
        #     t = f.readlines()
        #     t1 = t[0]

        # queryNew = ''
        # for i in range(0, len(t1)-2):
        #     queryNew = queryNew + t1[i]

        print('this :: ' + new_str)

    judge = judge if judge is not None else judge2
    s = Search(using=client)
    allfields = ['content', 'summary', 'judge', 'acts', 'title', 'verdict','keywords', 'appeal', 'verdict', 'subject']
    should =[]
    if(query is not None):
        q_base=Q('multi_match',query=new_str,fuzziness="1",prefix_length=3, fields=allfields)
        should.append(q_base)
    if(judge is not None):
        if(len(judge)>0):
            q_judge = Q('multi_match',query=judge,fields=['judge'])
            should.append(q_judge)
    if(acts is not None):
        q_acts = Q('multi_match',query=acts,fields=['acts'])
        should.append(q_acts)
    if(category is not None):
        q_category = Q('multi_match',query=category,fields=['subject'])
        should.append(q_category)
    if(date_from is not None and date_to is not None):
        q_date = Q('range',date={'gte':date_from,'lte':date_to,'format':"yyyy/MM/dd"})
        should.append(q_date)
    # if(date_from is None and date_to is not None):
    #     q_date = Q('range',fields=['date'],gte="1940/01/01",lte=date_to,format="yyyy/MM/dd")
    #     should.append(q_date)
    # if(date_from is not None and date_to is not None):
    #     q_date = Q('range',fields=['date'],gte=date_from,lte="now",format="yyyy/MM/dd")
    #     should.append(q_date)
    q = Q('bool',should=should,minimum_should_match=len(should))
    print(q)
    s=s.query(q)
    count=s.count()
    end = start + 20
    response = s[start:min(end, count)].execute()
    response= response.to_dict()
    result={}

    # global query_
    # query_ = query
    # query_ = query_.strip().split()
    # query_ = m.infer_vector(query_, alpha=start_alpha, steps=infer_epoch)

    for i in range(len(response['hits']['hits'])):
    	resp = response['hits']['hits'][i]["_source"]
    	resp['score']=response['hits']['hits'][i]["_score"]
    	result[str(i)]=resp
        resp.pop('content')
    result['count'] = count
    # result_ = result.values()
    # result_ = sorted(result_, key=functools.cmp_to_key(compare))
    # result = {}
    # for i in range(len(response['hits']['hits'])):
    #     result[str(i)]=result_[i]

    return json.dumps(result)

@app.route("/file")
def get_file():
    caseid=request.args.get('caseid')
    s=Search(using=client)
    q = Q('multi_match',query=caseid,fields=['caseid'])
    s=s.query(q)
    count=s.count()
    response = s[0:count].execute()
    response= response.to_dict()
    result={}
    for i in range(len(response['hits']['hits'])):
        resp = response['hits']['hits'][i]["_source"]
        resp['score']=response['hits']['hits'][i]["_score"]
        result[str(i)]=resp
    return json.dumps(result)


@app.route("/act")
def get_act():
    actid=request.args.get('actid')
    s=Search(using=client)
    q = Q('multi_match',query=actid,fields=['actid'])
    s=s.query(q)
    count=s.count()
    response = s[0:count].execute()
    response= response.to_dict()
    result={}
    for i in range(len(response['hits']['hits'])):
        resp = response['hits']['hits'][i]["_source"]
        resp['score']=response['hits']['hits'][i]["_score"]
        result[str(i)]=resp
    return json.dumps(result)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)