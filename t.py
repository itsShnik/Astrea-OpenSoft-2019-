import re

filenames = [ 'extracted_out.txt'] 
# filenames = [ 'EXTRACTED_7500_15000.txt']
with open('extracted.txt','w+') as f_:
	for file in filenames:
		with open(file,'r') as f:
			txt = re.sub("[,][\n]", ',', f.read())
			txt = re.sub("[a][r][r][a][y][\(][\[]", '[[]', txt)
			txt = re.sub("[d][t][y][p][e][=][f][l][o][a][t][3][2][\)][,]", '[]', txt)
			f_.write(txt)