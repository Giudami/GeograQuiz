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
SELECT ?country ?countryLabel ?capital ?capitalLabel ?flag ?popolation ?surface ?unicode ?map 
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

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
} ORDER BY DESC(?linkcount)
LIMIT 200
```
## Politici (senza label)
```
SELECT DISTINCT ?politician ?country WHERE {
  ?politician wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q82955;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
```
## Scienziati (senza label)
```
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
## Atleta (da rivedere, trova Putin, Bill Gates, ecc..)
```
SELECT DISTINCT ?athlete ?country WHERE {
  ?athlete wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q2066131;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
```
## Attori 
```
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
```
## Architetti
```
SELECT DISTINCT ?architect ?country WHERE {
  ?architect wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q42973;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
```
## Cantanti
```
SELECT DISTINCT ?singer ?country WHERE {
  ?singer wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q177220;
    wdt:P106/wdt:P279* wd:Q753110;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
  MINUS { 
    {?singer wdt:P106/wdt:P279* wd:Q49757.} UNION {?singer wdt:P106/wdt:P279* wd:Q55960555.} 
    }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
```
## Compositori
```
SELECT DISTINCT ?musician ?country WHERE {
  ?musician wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q36834;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
    MINUS { 
    {?musician wdt:P106/wdt:P279* wd:Q49757.} UNION {?musician wdt:P106/wdt:P279* wd:Q36180.} 
    }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
```
## Registi
```
SELECT DISTINCT ?filmDirector ?country WHERE {
  ?filmDirector wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q1414443;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
```
## Pittori
```
SELECT DISTINCT ?painter ?country WHERE {
  ?painter wdt:P31 wd:Q5;
    wdt:P106/wdt:P279* wd:Q1028181;
    wdt:P27 ?country;
    wikibase:sitelinks ?linkcount.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?linkcount)
LIMIT 200
```
