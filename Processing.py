import json
from SPARQLWrapper import SPARQLWrapper, JSON

with open('data.json', 'r') as data_file:
    data = json.load(data_file)

countries = [c["country"] for c in data]
for i in range(len(data)):
    data[i]["related"] = [r for r in data[i]["related"] if r in countries]


sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')

query = """
SELECT ?article WHERE {{
    ?article schema:about {0} .
    ?article schema:isPartOf <https://it.wikipedia.org/>.
    SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "it"
    }}
}}
"""
sparql.setReturnFormat(JSON)

for i in range(len(data)):
    print(countries[i])
    sparql.setQuery(query.format("<" + countries[i] + ">"))
    results = sparql.query().convert()
    data[i]["wikipedia"] = results["results"]["bindings"][0]["article"]["value"]
        
with open('data.json', 'wb') as data_file:
    data = json.dump(data, data_file)
