import os
from elasticsearch_dsl import Search,Q, UpdateByQuery
from elasticsearch import Elasticsearch
import ast
import commands

EXTRACTED_CASES_FILE = 'cases.json'

with open(EXTRACTED_CASES_FILE, 'r') as f:#store your cases.json file in the same directory as this script
	extracted_acts = ast.literal_eval(f.read())

with open('files.txt', 'r') as f:
	files = f.readlines()

ES_HOST   = {"host":"127.0.0.1","port":9200}
# client1 = Elasticsearch(hosts=[ES_HOST],index="test")
# client2 = Elasticsearch(hosts=[ES_HOST],index="index")
client = Elasticsearch(hosts=[ES_HOST])
s = Search(using=client)
ubq = UpdateByQuery(using=client)

start = 8811
x = ""
for i in range(start, len(files)):
	file = files[i]
	case = file.split('.')[0]
	print(i, case, '\n')
	if file.strip() not in extracted_acts or extracted_acts[file.strip()]==[""]:
		print('ignored')
		i += 1		
		continue
	x = "curl -XPOST \"localhost:9200/test/docs/" + str(i+1)
	x += '/_update\" -H \'Content-Type: application/json\' -d\' { "doc": {"acts" :'+ str([int(x) for x in extracted_acts[file.strip()]]) + '} }\''
	out = commands.getstatusoutput(x)[1]
	print(i, out)
	i += 1