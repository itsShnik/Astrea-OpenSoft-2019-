with open('Trial1.txt', 'r') as f:
	txt = f.readlines()

import json
out = {}

for i in range(0, len(txt), 2):
	out[txt[i].strip()] = txt[i+1].strip().replace(']', '[').replace('[', '').split(',')


with open('cases.json', 'w') as f:
	json.dump(out, f)