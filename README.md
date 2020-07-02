# GeograQuiz-

knowledge graphs - slide 14.18
information retrieval - slide 14

## Query SPARQL
Cerchiamo le città più simili a Roma
## Approccio 3 
### Versione WikiData
```
SELECT ?city (COUNT(?properties) AS ?commonsCount ) 
WHERE
{
wd:Q220 ?properties ?ontology .
?city wdt:P31 wd:Q1549591 ;
?properties ?ontology
FILTER (?city != wd:Q220).
} GROUP BY ?city
ORDER BY DESC(?commonsCount)
LIMIT 10
```
## Approccio 3 
### Versione DBpedia
```
SELECT COUNT(?p) ?country
WHERE
{
dbr:Italy ?p ?o .
?country rdf:type dbo:Country ;
?p ?o
FILTER (?country != dbr:Italy).
} GROUP BY ?country
ORDER BY DESC(COUNT(?p))
LIMIT 20
```
## Approccio 1
### Versione DBpedia
```
SELECT COUNT(?o) ?country
WHERE
{
dbr:Australia dct:subject ?o .
?country dct:subject ?o
FILTER (?country != dbr:Australia).
} GROUP BY ?country
ORDER BY DESC(COUNT(?o))
LIMIT 10
```


## Classifica giocatori di calcio
```
PREFIX vrank:<http://purl.org/voc/vrank#>
SELECT ?astronaut ?rank
FROM <http://dbpedia.org>
FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank>
WHERE {
?astronaut rdf:type dbo:Athlete, dbo:Person; <http://purl.org/linguistics/gold/hypernym> dbr:Footballer . 
?astronaut vrank:hasRank ?r .
?r vrank:rankValue ?rank .
} ORDER by DESC(?rank)
```


## Classifica piloti motosport
```
PREFIX vrank:<http://purl.org/voc/vrank#>
SELECT ?astronaut ?rank
FROM <http://dbpedia.org>
FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank>
WHERE {
?astronaut rdf:type dbo:Athlete, dbo:Person, dbo:MotorsportRacer. 
?astronaut vrank:hasRank ?r .
?r vrank:rankValue ?rank .
} ORDER by DESC(?rank)
```

## Tutti gli altri atleti
```
PREFIX vrank:<http://purl.org/voc/vrank#>
SELECT ?astronaut ?rank
FROM <http://dbpedia.org>
FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank>
WHERE {
?astronaut rdf:type dbo:Athlete, dbo:Person . 
?astronaut vrank:hasRank ?r .
?r vrank:rankValue ?rank .
MINUS {
     {?astronaut <http://purl.org/linguistics/gold/hypernym> dbr:Footballer} UNION {?astronaut rdf:type dbo:Athlete, dbo:Person, dbo:MotorsportRacer}
   }
} ORDER by DESC(?rank)
```

## Attori non vedi cosa scritto
non per essere razzisti, ma sono troppo presenti, e nel caso degli indiani troppo sconosciuti fuori dall'india
```
PREFIX vrank:<http://purl.org/voc/vrank#>
SELECT ?astronaut ?rank ?nationality
FROM <http://dbpedia.org>
FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank>
WHERE {
?astronaut <http://purl.org/linguistics/gold/hypernym> dbr:Actor.
?astronaut vrank:hasRank ?r .
?r vrank:rankValue ?rank . 
?astronaut dbp:nationality ?nationality 
filter (
?nationality != "American"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString> && 
?nationality != "British"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString> && 
?nationality != "Indian"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString> &&
?nationality != "Japanese"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString> &&
?nationality != "Canadian"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString> &&
 ?nationality != "English"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString>)
} ORDER by DESC(?rank)
```
## Stati per importanza
```
PREFIX vrank: <http://purl.org/voc/vrank#>

SELECT ?country ?countryLabel ?capital ?capitalLabel ?flag ?popolation ?surface ?unicode ?map ?rank

WHERE
{
  ?country wdt:P31 wd:Q3624078 .
  #not a former country
  FILTER NOT EXISTS {?country wdt:P31 wd:Q3024240}
  #and no an ancient civilisation (needed to exclude ancient Egypt)
  FILTER NOT EXISTS {?country wdt:P31 wd:Q28171280}
   ?country wdt:P36 ?capital  .
   ?country wdt:P41 ?flag .
   ?country wdt:P1082 ?popolation .
   ?country wdt:P2046 ?surface  .
   ?country wdt:P487 ?unicode  .
   ?country wdt:P242 ?map  .
   ?country wikibase:sitelinks ?linkcount .
  SERVICE <http://dbpedia.org/sparql> {
      ?country vrank:hasRank/vrank:rankValue ?rank .
  }  

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
} ORDER BY DESC(?linkcount)
```
