# GeograQuiz-

knowledge graphs - slide 14.18
information retrieval - slide 14

## Query SPARQL
Cerchiamo le città più simili a Roma
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
