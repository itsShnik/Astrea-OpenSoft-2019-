from elasticsearch import Elasticsearch,exceptions
import ast
import sys

def connect(filename, indexname, doc_type):
    ES_HOST   = {"host":"localhost","port":9200}
    es = Elasticsearch(hosts=[ES_HOST])
    INDEX_NAME = indexname
    try:
        response = es.indices.create(index=INDEX_NAME,body={"settings":{"analysis":{"analyzer":{"default":{"type":"english"}}}}})
    except exceptions.RequestError:
        print("Index Already Created")
        return
    print(response)
    db = open(filename)
    lists = db.readlines()
    i=1
    for line in lists:
        body = ast.literal_eval(line)
        resp = es.index(index=INDEX_NAME,doc_type=doc_type,body=body,id=i)
        i=i+1
        print(resp)


if __name__ == "__main__":
    connect(sys.argv[1],sys.argv[2],sys.argv[3])