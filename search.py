from elasticsearch_dsl import Search,Q
from elasticsearch import Elasticsearch

ES_HOST   = {"host":"localhost","port":9200}
client = Elasticsearch(hosts=[ES_HOST])

s = Search(using=client)
q=Q('multi_match',query='Mahajan murder')
s=s.query(q)
count=s.count()
response = s[0:count].execute()
for i in response:
    print(i.summary)