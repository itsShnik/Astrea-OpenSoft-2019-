with open('subject_keywords.txt', 'r') as f:
	txt = f.readlines()

import json
out = {}
i = 0
for line in txt:
	print(i)
	case, _, sub_keys = line.split('-->')
	sub_keys.lstrip()
	if '$$$' not in sub_keys:
		continue
	sub, keys = sub_keys.split('$$$')
	sub = [i.lstrip() for i in sub.lstrip().split(';')]
	keys.lstrip()
	out[case] = {'subject': sub, 'keywords': keys.rstrip()}
	i += 1
	print(case)

with open('keywords.json', 'w') as f:
	json.dump(out, f)