from elasticsearch import Elasticsearch,exceptions
import ast
import sys
import os

FILELOC = 'extracted/'
#usage >  python db_gen.py out.txt test docs 

def connect(dirname, indexname, doc_type):
    ES_HOST   = {"host":"localhost","port":9200}
    es = Elasticsearch(hosts=[ES_HOST])
    INDEX_NAME = indexname
    # try:
    if not es.indices.exists(index=INDEX_NAME):
        response = es.indices.create(index=INDEX_NAME,body={"settings":{"analysis":{"analyzer":{"default":{"type":"english"}}}}})
        print(response)
    # except exceptions.RequestError:
    #     print("Index Already Created")
    #     return
    files = os.listdir(FILELOC)
    files.sort()
    i=1
    
    for file in files:
        with open(FILELOC + file, 'r') as f:
            lists = f.readlines()
        
        for line in lists:
            body = ast.literal_eval(line)
            resp = es.index(index=INDEX_NAME,doc_type=doc_type,body=body, id= i )
            i=i+1
            print(resp)


if __name__ == "__main__":
    connect(sys.argv[1],sys.argv[2],sys.argv[3])