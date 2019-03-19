from flask import Flask,request
from elasticsearch_dsl import Search,Q
from elasticsearch import Elasticsearch
import json


ES_HOST   = {"host":"localhost","port":9200}
client = Elasticsearch(hosts=[ES_HOST])


app = Flask(__name__)

@app.route("/")
def welcome():
    return ("Server Started")

@app.route("/search")
def search():
    query=request.args.get('q')
    judge=request.args.get('judge')
    category=request.args.get('category')
    acts=request.args.get('acts')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    s = Search(using=client)
    should =[]
    if(query is not None):
        q_base=Q('multi_match',query=query,fuzziness="1",prefix_length=3)
        should.append(q_base)
        judge = request.args.get('judge')
    if(judge is not None):
        q_judge = Q('multi_match',query=judge,fields=['Judge'])
        should.append(q_judge)
    if(acts is not None):
        q_acts = Q('multi_match',query=acts,fields=['Judge'])
        should.append(q_acts)
    if(category is not None):
        q_category = Q('multi_match',query=category,fields=['Judge'])
        should.append(q_category)
    if(date_from is not None and date_to is not None):
        q_date = Q('range',fields=['Date'],gte=date_from,lte=date_to,format="yyyy/MM/dd")
        should.append(q_date)
    if(date_from is None and date_to is not None):
        q_date = Q('range',fields=['Date'],gte="1940/01/01",lte=date_to,format="yyyy/MM/dd")
        should.append(q_date)
    if(date_from is not None and date_to is not None):
        q_date = Q('range',fields=['Date'],gte=date_from,lte="now",format="yyyy/MM/dd")
        should.append(q_date)
    q = Q('bool',should=should,minimum_should_match=len(should))
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