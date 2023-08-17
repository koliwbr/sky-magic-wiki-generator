import json


raw = json.load(open('raw-mapping.json'))
v = json.load(open('vanila_items.json'))

out = {}
v2 = {}
for data in v:
	v2[data['displayName']] = data['name']


for name, posdata in raw['ids'].items():
	if v2.get(name):
		out[v2.get(name)] = posdata['pos']
print(json.dumps(out))
