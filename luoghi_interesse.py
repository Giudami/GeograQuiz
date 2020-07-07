import json
from SPARQLWrapper import SPARQLWrapper, JSON

with open('data.json', 'r') as data_file:
    data = json.load(data_file)
# vogliamo ottenere i luoghi di interesse relativi ad ogni nazione
sparql = SPARQLWrapper("https://dbpedia.org/sparql")

query = """
PREFIX vrank:<http://purl.org/voc/vrank#>
select ?thingWikidata
FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank>
where {{
?country owl:sameAs {0}.
?thing dbo:location ?country.
?thing owl:sameAs ?thingWikidata .
?thing vrank:hasRank ?r .
?r vrank:rankValue ?rank .
FILTER(strstarts(str(?thingWikidata),str(wikidata:))).
optional
{{
?thing a ?type.
VALUES ?type {{dbo:NaturalPlace}}
BIND( "NaturalPlace" as ?typeName )
}}
optional
{{
?thing a ?type.
VALUES ?type {{dbo:Venue}}
BIND( "Venue" as ?typeName )
}}
optional
{{
?thing a ?type.
VALUES ?type {{dbo:Museum}}
BIND( "Museum" as ?typeName )
}}
optional
{{
?thing a ?type.
VALUES ?type {{dbo:Pyramid}}
BIND( "Pyramid" as ?typeName )
}}
optional
{{
?thing a ?type.
VALUES ?type {{yago:Skyscraper104233124}}
BIND( "Skyscraper" as ?typeName )
}}
optional
{{
?thing a ?type.
VALUES ?type {{dbo:Park}}
BIND( "Park" as ?typeName )
}}
optional
{{
?thing a ?type.
VALUES ?type {{dbo:ReligiousBuilding}}
BIND( "ReligiousBuilding" as ?typeName )
}}
{{
?thing a dbo:Place
}}
filter (BOUND (?type))
}} ORDER by DESC(?rank) LIMIT 12
"""

sparql.setReturnFormat(JSON)

array = []

for result in data:
    sparql.setQuery(query.format("<" + result["country"] + ">"))
    results = sparql.query().convert()
    for i in range(0, len(results["results"]["bindings"])):
        array.append(results["results"]["bindings"]
                     [i]["thingWikidata"]["value"])
    result["pointsOfInterest"] = array
    array = []

with open('data2.json', 'wb') as f:
    data = json.dump(data, f)
