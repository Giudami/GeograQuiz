import json
import random

optionsNumber = 3

countries = None
countriesCount = 0
URIforIndex = []

with open("./assets/query.json") as input:
    countries = json.load(input)
    countriesCount = len(countries)
    for country in countries:
        URIforIndex.append(country["country"])

    # print(list(filter(lambda elem: elem["country"] == "http://www.wikidata.org/entity/Q33", data))


def randomElems(elems, n):
    return [elems[i] for i in random.sample(range(len(elems)), n)]


def mapQuestion():
    countryIndex = random.randrange(countriesCount)
    country = countries[countryIndex]
    mapIndex = random.randrange(len(country["maps"]))
    image = country["maps"][mapIndex]
    options = randomElems(country["related"], optionsNumber)
    options.append(country["country"])
    result = {"title": "Qual è la nazione in figura?",
              "image": image, "options": options, "correct": country["country"]}
    print(result)


def countryForCapitalQuestion():
    countryIndex = random.randrange(countriesCount)
    country = countries[countryIndex]
    options = randomElems(country["related"], optionsNumber)
    options.append(country["country"])
    result = {"title": country["capitalLabel"] + " è la capitale di quale tra le seguenti nazioni?",
              "options": options, "correct": country["country"]}
    print(result)


def svg2png(svg):
    return svg


countryForCapitalQuestion()

# http://www.wikidata.org/entity/Q33
