import json
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')

sparql.setQuery("""
 SELECT ?country ?countryLabel ?capital ?capitalLabel ?flag ?population ?surface ?unicode ?maps
WHERE
{
  ?country wdt:P31 wd:Q3624078 .
  #not a former country
  FILTER NOT EXISTS {?country wdt:P31 wd:Q3024240}
  #and no an ancient civilisation (needed to exclude ancient Egypt)
  FILTER NOT EXISTS {?country wdt:P31 wd:Q28171280}
   ?country wdt:P36 ?capital  .
   ?country wdt:P41 ?flag .
   ?country wdt:P1082 ?population .
   ?country wdt:P2046 ?surface  .
   ?country wdt:P487 ?unicode  .
   ?country wdt:P242 ?maps  .
   ?country wikibase:sitelinks ?linkcount . 

  SERVICE wikibase:label { bd:serviceParam wikibase:language "it" }
} ORDER BY DESC(?linkcount)
""")

sparql.setReturnFormat(JSON)

results = sparql.query().convert()
maps_array = []
final_results = []
maps_array.append(results["results"]["bindings"][0]["maps"]["value"])
for i in range(1, len(results["results"]["bindings"])):
  r1 = results["results"]["bindings"][i-1]
  r2 = results["results"]["bindings"][i]
  if r1["country"]["value"] == r2["country"]["value"]:
    maps_array.append(r2["maps"]["value"])
  else:
    r1["maps"]["value"] = maps_array
    final_results.append(r1)
    maps_array = [r2["maps"]["value"]]

results["results"]["bindings"][-1]["maps"]["value"] = maps_array
final_results.append(results["results"]["bindings"][-1])
for result in final_results:
  result["maps"] = result["maps"]["value"]
  result["capitalLabel"] = result["capitalLabel"]["value"]
  result["country"] = result["country"]["value"]
  result["surface"] = result["surface"]["value"]
  result["flag"] = result["flag"]["value"]
  result["unicode"] = result["unicode"]["value"]
  result["capital"] = result["capital"]["value"]
  result["population"] = result["population"]["value"]
  result["countryLabel"] = result["countryLabel"]["value"]

sparql = SPARQLWrapper("https://dbpedia.org/sparql")

query = """
SELECT ?countryWikidata
WHERE
{{
?key owl:sameAs {0}.
?key ?p ?o .
?country rdf:type dbo:Country ;
?p ?o .
?country owl:sameAs ?countryWikidata .
FILTER(strstarts(str(?countryWikidata),str(wikidata:))).
FILTER (?country != ?key).
}} GROUP BY ?countryWikidata
ORDER BY DESC(COUNT(?p))
LIMIT 8
"""

sparql.setReturnFormat(JSON)

related_array = []

for result in final_results:
  sparql.setQuery(query.format("<" + result["country"] + ">"))
  results = sparql.query().convert()
  for i in range(0, len(results["results"]["bindings"])):
    related_array.append(results["results"]["bindings"][i]["countryWikidata"]["value"])
  print(related_array)
  result["related"] = related_array
  related_array = []

with open('data.json', 'wb') as f:
  json.dump(final_results, f)
