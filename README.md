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
