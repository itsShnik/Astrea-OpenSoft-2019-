from elasticsearch import Elasticsearch,exceptions
import ast
import sys
import json
import os

#usage >  python db_gen.py out.txt test docs 

def connect(filename, indexname, doc_type):
    ES_HOST   = {"host":"localhost","port":9200}
    es = Elasticsearch(hosts=[ES_HOST])
    INDEX_NAME = indexname
    # try:
    if not es.indices.exists(index="index"):
        response = es.indices.create(index=INDEX_NAME,body={"settings":{"analysis":{"analyzer":{"default":{"type":"english"}}}}})
    # except exceptions.RequestError:
    #     print("Index Already Created")
    #     return
        print(response)

    i=0
    ignore = 0
    ignored = []
    with open(filename,"r") as f:
        lists = f.readlines()
    for line in lists:
        body = ast.literal_eval(line)
        body = json.dumps(body,encoding='utf-8',ensure_ascii=False)
        try:
            resp = es.index(index=INDEX_NAME,doc_type=doc_type,body=body,id=i )
        except:
            print('Ignoring', body)
            ignore += 1
            ignored.append(body)
        i=i+1
        print(resp)

    # print(ignored)
    print(ignore, 'documents ignored')


if __name__ == "__main__":
    connect(sys.argv[1],sys.argv[2],sys.argv[3])
