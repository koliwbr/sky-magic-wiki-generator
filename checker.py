#!/bin/env python3

namespace = 'skymagic'

import json

vanilla_items = {}

for item in json.load(open('vanila_items.json')):
	vanilla_items[item['name']] = item['displayName']

warnings = []
errors = []

for item, data in json.load(open(f'items/{namespace}.json')).items():
	assert data.get('id') # check if ID exist and is not empty
	assert type(data['id']) == str # check if ID is string
	assert data['id'].split(':',1)[0] == 'minecraft' # check if ID is in minecft name space

	assert not data.get('nbt') is None # check if NBT exist
	assert type(data['nbt']) == dict # check if ID is dict

	base_item_id = data['id'].split(":",1)[1]
	assert vanilla_items.get(base_item_id) # check if base item exist in minecraft


	item_display = data.get('nbt',{}).get('display',{}).get('Name')
	display_name = None
	if item_display:
		display_name = json.loads(item_display).get('text')

	if not len(data.get('nbt')):
		warnings.append(f"{namespace}:{item} => Empty NBT!")
	if not data.get('nbt',{}).get('Tags'):
		warnings.append(f"{namespace}:{item} => No tags!")
	if not display_name:
		warnings.append(f"{namespace}:{item} => No Custome Name!")

	print(f"{display_name} ({namespace}:{item})")
	print(f"\tTrue item: {vanilla_items.get(base_item_id)} (minecraft:{base_item_id})")
	print(f"\tTags: {data.get('nbt',{}).get('Tags')}")


print()
for warn in warnings:
	print(f"\033[31mWARN: {warn}\033[39m")

if warnings:
	exit(2)