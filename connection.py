import json
from SPARQLWrapper import SPARQLWrapper, JSON

# per ottenere tempi di timeout piu' lunghi
# modifichiamo l'user agent
sparql = SPARQLWrapper("https://query.wikidata.org/sparql",
                       agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')

# settiamo la query necessaria per ottenere le informazioni
sparql.setQuery("""
 SELECT ?country ?countryLabel ?capital ?capitalLabel ?flag ?population ?surface ?unicode ?maps ?article
WHERE
{
  # per includere gli stati sovrani
  ?country wdt:P31 wd:Q3624078 .
  # per escludere le ex nazioni
  FILTER NOT EXISTS {?country wdt:P31 wd:Q3024240}
  # per escludere gli stati dei popoli antichi
  FILTER NOT EXISTS {?country wdt:P31 wd:Q28171280}
   ?country wdt:P36 ?capital  .
   ?country wdt:P41 ?flag .
   ?country wdt:P1082 ?population .
   ?country wdt:P2046 ?surface  .
   ?country wdt:P487 ?unicode  .
   ?country wdt:P242 ?maps  .
   ?article schema:about ?country .
   ?article schema:isPartOf <https://it.wikipedia.org/>.
   ?country wikibase:sitelinks ?linkcount . 
  # utilizziamo l'italiano come lingua
  SERVICE wikibase:label { bd:serviceParam wikibase:language "it" }
} ORDER BY DESC(?linkcount) # ordiniamo grazie al linkcount
""")

# formato di default XML noi lo settiamo a JSON che viene restituito come JSON decorato
sparql.setReturnFormat(JSON)
# otteniamo i risultati della query
results = sparql.query().convert()
maps_array = []
final_results = []
# otteniamo le URI relative alle mappe e le inseriamo in maps_array
maps_array.append(results["results"]["bindings"][0]["maps"]["value"])
# operiamo per ottenere un solo stato con piu' mappe (altrimenti lo stesso stato con mappa diversa viene riconosciuto come entita' diversa)
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
# trasformiamo il nostro JSON decorato in JSON non decorato per operare in maniera migliore
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
    result["article"] = result["article"]["value"]

# settiamo l'endpoint a DBpedia per la prossima query
sparql = SPARQLWrapper("https://dbpedia.org/sparql")
# prepariamo la prossima query
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
# otteniamo i correlati di ogni paese e trasformiamo direttamente in JSON non decorato
for result in final_results:
    # query.format ci permette di modificare il valore {0} presente nella query
    sparql.setQuery(query.format("<" + result["country"] + ">"))
    results = sparql.query().convert()
    for i in range(0, len(results["results"]["bindings"])):
        related_array.append(
            results["results"]["bindings"][i]["countryWikidata"]["value"])
    print(related_array)
    result["related"] = related_array
    related_array = []
# creiamo il nostro file data.json su cui andremo a scrivere i risultati ottenuti
with open('data.json', 'wb') as f:
    json.dump(final_results, f)
