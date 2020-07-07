## PROGETTO TECNICHE PER LA GESTIONE DEGLI OPEN DATA A.A. 2019/2020

### GeograQuiz

​																	**Davide Avellone, matricola:0670611**
																	 **Michele Sanfilippo, matricola: 0664184**
																	 **Giuseppe Marino, matricola:0664577**

### **Introduzione**

Il progetto ha come obiettivo quello di creare un dataset riguardante dati geografici sulla base delle informazioni ottenute da Wikidata e DBpedia, e successivamente utilizzare questo dataset come base di conoscenza per un bot Telegram sviluppato in Python. Tale bot sarà utilizzabile soltanto da gruppi Telegram e attraverso i dati ottenuti creerà dei quiz geografici con opportune possibilità di risposta. 

Wikidata mette a disposizione i propri dati con licenza CC0, mentre DBpedia con licenza CC-BY-SA ShareAlike 3.0. Quindi i dati utilizzati da Wikidata sono compatibili con qualsiasi altra licenza, mentre quelli di DBpedia soltanto con licenze CC-BY-SA, a tal proposito il nostro dataset sarà rilasciato con una licenza di tipo CC-BY-SA per mantenere la compatibilità.

### **Dataset**

Il dataset utilizzato è stato opportunamente realizzato da noi ricavando le informazioni da Wikidata e DBpedia attraverso i loro rispettivi endpoint ed utilizzando query in formato SPARQL con la libreria SPARQLWrapper:

```python
https://query.wikidata.org/sparql 
https://dbpedia.org/sparql
```

Nello specifico abbiamo sfruttato questi endpoint per ottenere informazioni riguardanti i vari Paesi del mondo (dai quali dobbiamo escludere le civiltà antiche o paesi non riconosciuti) : capitale, bandiera, popolazione, superficie, unicode e mappe. I Paesi ottenuti saranno ordinati attraverso un linkcount (che ci permette di capire quali paesi hanno più informazioni e quindi sono più rilevanti) per averli dal più significativo al meno significativo. 
La query risulta essere la seguente:

```SPARQL
SELECT ?country ?countryLabel ?capital ?capitalLabel ?flag ?population ?surface ?unicode ?maps

WHERE
{
 ?country wdt:P31 wd:Q3624078 .
 \#not a former country
 FILTER NOT EXISTS {?country wdt:P31 wd:Q3024240}
 \#and no an ancient civilisation (needed to exclude ancient Egypt)
 FILTER NOT EXISTS {?country wdt:P31 wd:Q28171280}
  ?country wdt:P36 ?capital .
  ?country wdt:P41 ?flag .
  ?country wdt:P1082 ?population .
  ?country wdt:P2046 ?surface .
  ?country wdt:P487 ?unicode .
  ?country wdt:P242 ?maps .
  ?country wikibase:sitelinks ?linkcount . 
 SERVICE wikibase:label { bd:serviceParam wikibase:language "it" }
} ORDER BY DESC(?linkcount)
```

Attualmente siamo in possesso dei Paesi che ci interessano con le loro proprietà. Siamo interessati, al fine di ottenere delle alternative coerenti con le risposte corrette dei quiz, a ricercare, per ogni Paese presente nella query, una lista di Paesi ad esso correlati. Con correlati intendiamo quei Paesi che più sono simili al Paese soggetto del quiz, ad esempio se sarà presente una domanda sull'Italia vogliamo che le alternative siano Paesi "simili" all'Italia (ad esempio Spagna, Francia... piuttosto che Congo, Corea del Nord...) per avere quiz più coerenti. 
Per implementare questa logica della correlazione abbiamo utilizzato la seguente query processata in Python:

```SPARQL
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
```

In questa query utilizziamo la similarità di DBpedia attraverso  le URI di Wikidata e otteniamo le informazioni dei paesi correlati sotto forma di URI di Wikidata. Viene utilizzato **{0}** poiché il Paese di cui vogliamo i correlati deve variare. Esso prende il proprio valore attraverso: 

```python
sparql.setQuery(query.format("<" + result["country"] + ">"))
```

dove **result["country"]** conterrà la URI di Wikidata.

Allo stesso abbiamo lavorato con la query per ottenere la pagina wikipedia del paese soggetto, la quale viene utilizzata per i suggerimenti nel bot:
```SPARQL
SELECT ?article WHERE {{
    ?article schema:about {0} .
    ?article schema:isPartOf <https://it.wikipedia.org/>.
    SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "it"
    }}
}}
```

Sono state elaborate anche altre query per ottenere più informazioni riguardanti i Paesi. Ad esempio query per gli scienziati, i politici, gli atleti, gli attori, gli architetti, ecc. e per i luoghi di interesse, come musei, parchi, chiese, stadi, ecc.

```SPARQL
#CALCIATORI FAMOSI
PREFIX vrank:<http://purl.org/voc/vrank#>
SELECT ?footballer ?rank
FROM <http://dbpedia.org>
FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank>
WHERE {
?footballer rdf:type dbo:Athlete, dbo:Person; <http://purl.org/linguistics/gold/hypernym> dbr:Footballer . 
?footballer vrank:hasRank ?r .
?r vrank:rankValue ?rank .
} ORDER by DESC(?rank)
```



```SPARQL
#ATTORI
SELECT DISTINCT ?actor ?country WHERE {
  ?actor wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q10800557;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
  MINUS{
    {?actor wdt:P106/wdt:P279* wd:Q639669.} UNION { ?actor wdt:P106/wdt:P279* wd:Q36180.}
    }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
#il MINUS per escludere quei musicisti e scrittori che erano apparsi in qualche film
```



```SPARQL
#SCIENZIATI
SELECT DISTINCT ?scientist ?country WHERE {
  ?scientist wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q901;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
```

Queste query dovevano essere utilizzate per ogni paese, quindi al variare del paese avremmo dovuto ottenere scienziati, calciatori, attori e persone famose in generale relative a quel dato paese ordinate rispetto al linkcount. 
Il problema che sorge è che nel caso in cui il paese soggetto sia un Paese poco conosciuto dalla media (ad esempio il Brunei) potrebbe succedere che esso non abbia scienziati o altri personaggi famosi di particolare rilevanza tanto da non essere presenti in Wikidata, ma anche nel caso in cui siano presenti si nota che è difficile, a meno di tirare a sorte, indovinare la risposta esatta. Pertanto è stato ritenuto più opportuno non utilizzare queste query e di conseguenza questi dati non sono stati aggiunti al dataset.

La seguente, invece, è la query per i luoghi di interesse. Si è pensato di far variare i paesi e prendere 12 dei luoghi di interesse più famosi per quel paese. Nell'esempio sotto il paese viene fissato a Spain.

```SPARQL
#LUOGHI DI INTERESSE
PREFIX vrank:<http://purl.org/voc/vrank#>
select ?thingWikidata ?thing ?typeName
FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank>
where {
VALUES ?country {<http://dbpedia.org/resource/Spain>}
?thing dbo:location ?country.
?thing owl:sameAs ?thingWikidata .
?thing vrank:hasRank ?r .
?r vrank:rankValue ?rank .
FILTER(strstarts(str(?thingWikidata),str(wikidata:))).
optional
{
?thing a ?type.
VALUES ?type {dbo:NaturalPlace}
BIND( "NaturalPlace" as ?typeName )
}
optional
{
?thing a ?type.
VALUES ?type {dbo:Venue}
BIND( "Venue" as ?typeName )
}
optional
{
?thing a ?type.
VALUES ?type {dbo:Museum}
BIND( "Museum" as ?typeName )
}
optional
{
?thing a ?type.
VALUES ?type {dbo:Pyramid}
BIND( "Pyramid" as ?typeName )
}
optional
{
?thing a ?type.
VALUES ?type {yago:Skyscraper104233124}
BIND( "Skyscraper" as ?typeName )
}
optional
{
?thing a ?type.
VALUES ?type {dbo:Park}
BIND( "Park" as ?typeName )
}
optional
{
?thing a ?type.
VALUES ?type {dbo:ReligiousBuilding}
BIND( "ReligiousBuilding" as ?typeName )
}
{
?thing a dbo:Place
}
filter (BOUND (?type))
} ORDER by DESC(?rank) LIMIT 12
```

L'output della query è il seguente:

![photo_2020-07-06_16-16-12](./img/photo_2020-07-06_16-16-12.jpg)

Non abbiamo utilizzato i risultati nel nostro dataset poiché avendo 195 paesi nel caso in cui venga estratto un paese poco conosciuto (il che è molto probabile, perché di questi 195 paesi quelli molto noti dalla media sono una minima parte) non si è in grado di associare il luogo di interesse al paese corretto.

### Pipeline di elaborazione

Abbiamo elaborato i dati ottenuti dalle query attraverso degli script in Python, in modo da ottenere dei file JSON utilizzabili dal bot come base di conoscenza. In particolare abbiamo agito sulle mappe e sui correlati di ogni paese. 

Per quanto riguarda le mappe, per alcuni paesi, wikidata ci forniva più di una mappa e questo creava dei conflitti in quanto il paese veniva riconosciuto più volte dato che le informazioni differivano per la mappa, e quindi venivano riconosciuti come paesi diversi. Pertanto abbiamo realizzato uno script che ci ha permesso di raggruppare le mappe differenti per un paese in una lista per la stessa entità piuttosto che per più entità diverse.

```python
#SCRIPT MAPPE
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
```

 Per raggruppare le mappe di un paese in una lista accediamo ai vari campi dell'entità fino ad arrivare alla mappa, e controlliamo se il paese dell'elemento successivo a quello che stiamo analizzando è uguale, e nel caso in cui lo è aggiungiamo la mappa alla lista delle mappe di quel paese ignorando successivamente il paese da cui abbiamo preso la mappa, altrimenti continuiamo la scansione, procedendo allo stesso modo. 

Per quanto riguarda i correlati sono stati aggiunti in un secondo momento attraverso uno script, che è il seguente:

```python
#SCRIPT CORRELATI
related_array = []

for result in final_results:
  sparql.setQuery(query.format("<" + result["country"] + ">"))
  results = sparql.query().convert()
  for i in range(0, len(results["results"]["bindings"])):
    related_array.append(results["results"]["bindings"][i]["countryWikidata"]["value"])
  print(related_array)
  result["related"] = related_array
  related_array = []
```

Dato il problema precedente delle mappe, si è deciso di creare direttamente related come lista di paesi correlati, che inizialmente ne conteneva 8 per ogni paese, ma successivamente è stato necessario filtrare questa lista e riportare i paesi correlati tra i paesi presenti nel dataset. Sono quindi stati eliminati dai correlati quei paesi che risultavano essere paesi non riconosciuti o territori contesi. 

```python
countries = [c["country"] for c in data]
for i in range(len(data)):
    data[i]["related"] = [r for r in data[i]["related"] if r in countries]
```

Per aggiungere i dati di wikipedia al JSON abbiamo invece utilizzato il seguente script:
```python
for i in range(len(data)):
    print(countries[i])
    sparql.setQuery(query.format("<" + countries[i] + ">"))
    results = sparql.query().convert()
    data[i]["wikipedia"] = results["results"]["bindings"][0]["article"]["value"]
```

I dati sono stati rappresentati in formato JSON, inizialmente decorato, e successivamente elaborato in python per renderlo non decorato e ideale per l'utilizzo del nostro bot. Questa elaborazione del JSON è stata fatta nel seguente modo:

```python
#ESEMPIO JSON DECORATO
"results": {
    "bindings": [
      {
        "country": {
          "type": "uri",
          "value": "http://www.wikidata.org/entity/Q17"
        },
        "flag": {
          "type": "uri",
          "value": "http://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20Japan.svg"
        },
        "unicode": { "type": "literal", "value": "🇯🇵" },
        "capital": {
          "type": "uri",
          "value": "http://www.wikidata.org/entity/Q1490"
        },
        "maps": {
          "type": "uri",
          "value": "http://commons.wikimedia.org/wiki/Special:FilePath/Japan%20on%20the%20globe%20%28de-facto%29%20%28Japan%20centered%29.svg"
        },
        "surface": {
          "datatype": "http://www.w3.org/2001/XMLSchema#decimal",
          "type": "literal",
          "value": "377972.28"
        },
        "population": {
          "datatype": "http://www.w3.org/2001/XMLSchema#decimal",
          "type": "literal",
          "value": "126785797"
        },
        "countryLabel": {
          "xml:lang": "it",
          "type": "literal",
          "value": "Giappone"
        },
        "capitalLabel": {
          "xml:lang": "it",
          "type": "literal",
          "value": "Tokyo"
        }
      }
```

```python
#ESEMPIO DA JSON DECORATO A NON DECORATO
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
```

Dopo l'elaborazione in python otteniamo i dati nel seguente formato:

```python
#ESEMPIO JSON NON DECORATO
{
    "capitalLabel": "Tokyo",
    "country": "http://www.wikidata.org/entity/Q17",
    "surface": "377972.28",
    "maps": [
      "http://commons.wikimedia.org/wiki/Special:FilePath/Japan%20on%20the%20globe%20%28de-facto%29%20%28Japan%20centered%29.svg"
    ],
    "flag": "http://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20Japan.svg",
    "related": [
      "http://www.wikidata.org/entity/Q884",
      "http://www.wikidata.org/entity/Q148",
      "http://www.wikidata.org/entity/Q30",
      "http://www.wikidata.org/entity/Q159",
      "http://www.wikidata.org/entity/Q142",
      "http://www.wikidata.org/entity/Q423"
    ],
    "unicode": "\ud83c\uddef\ud83c\uddf5",
    "capital": "http://www.wikidata.org/entity/Q1490",
    "countryLabel": "Giappone",
    "population": "126785797"
  }
```

### Bot Telegram
