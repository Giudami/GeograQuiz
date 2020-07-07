import json
from SPARQLWrapper import SPARQLWrapper, JSON
# lavoriamo sui correlati di ogni nazione per un filtraggio
# vogliamo che i correlati siano riportati tra le 195 nazioni presenti nel dataset
with open('data.json', 'r') as data_file:
    data = json.load(data_file)
# otteniamo le URI
countries = [c["country"] for c in data]
# operiamo
for i in range(len(data)):
    # se viene trovato manteniamo l'informazione
    data[i]["related"] = [r for r in data[i]["related"] if r in countries]
