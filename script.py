import json

with open('data.json', 'r') as data_file:
    data = json.load(data_file)

countries = [c["country"] for c in data]
for i in range(len(data)):
    data[i]["related"] = [r for r in data[i]["related"] if r in countries]

with open('data.json', 'wb') as data_file:
    data = json.dump(data, data_file)