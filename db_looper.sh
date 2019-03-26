#!/bin/sh

cd extracted/

for f in *; do
	echo $f
	python3 ../db_gen.py $f test docs
done
# cat -- !(user1.txt) 