## Steps to Start Server 

Start Elasticsearch from /bin path

### If Database isn't populated
---
Use db_gen.py script to populate db to Elasticcsearch

    usage : python db_gen.py <Extracted JSON> <Index Name> <Doc Name>

### After DB Is populated
---
Set FLASK_APP environment variable
    
    export FLASK_APP=server.py

Run flask

    flask run
You can also do

    env FLASK_APP=server.py flask run
    
### Send Query and Filter Values

    ..../search?q = query input by user in search box
                judge = judges name selected by user in filter, multiple names given seperated by spaces
                category = category input from filter
                acts = serial number or index of the acts selected in given acts list
                from = datefrom in format "yyyy/MM/dd"
                to = date to in format "yyyy/MM/dd"
                
    ..../file?caseid = caseid to request json of certain case
