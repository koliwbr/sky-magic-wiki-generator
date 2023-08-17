#!/bin/env python3

namespace = 'skymagic'

import json

vanilla_items = {}


for item in json.load(open('vanila_items.json')):
	vanilla_items[item['name']] = item['displayName']

warnings = []

def check(item, data):
	assert type(data.get('id')) == str # check if ID exist, is string exist and is not empty
	item_id = data['id'].removeprefix('minecraft:')
	assert vanilla_items.get(item_id) # check if base item exist in minecraft

	if not data.get('CustomModelData'):
		warnings.append(f"{namespace}:{item} => No CustomModelData!")

def gen_give_command(item,nbt):
	return f'give @s {item}{{{nbt}}}'

def get_display_name(item_name):
	return ' '.join([word[0].upper()+word[1::] for word in item_name.split('_')])

def gen_nbt(item,data):
	nbt = []
	nbt.append('display:{"Name":"{\\"text\\":\\"'+get_display_name(item)+'\\",\\"italic\\":false}"}')
	nbt.append(f'Tags:["{get_display_name(item)}"]')
	if data.get('CustomModelData'):
		nbt.append(f'CustomModelData:{data.get("CustomModelData")}')
	# nbt.append("Enchantments:[]")
	return ','.join(nbt)


crafting_items = {}
for item in vanilla_items.keys():
	crafting_items[f'minecraft:{item}'] = f'id: "minecraft:{item}"'

for item, data in json.load(open(f'items/{namespace}.json')).items():
	check(item, data)
	display_name = get_display_name(item)
	crafting_items[f"{namespace}:{item}"] = f'id:"minecraft:{data["id"]}",tag:{{Tags:["{display_name}"]}}'

	print(gen_give_command(data['id'],gen_nbt(item,data)))
	# print(f"{namespace}:{item}{{{gen_nbt(item,data)}}}")

for warn in warnings:
	print(f"\033[31mWARN: {warn}\033[39m")

# if warnings:
# 	exit(2)

workstations = [
	('magic_table',9)
]

print()

for output, data in json.load(open(f'craftings.json')).items():
	if data.get('count') is None:
		data['count'] = 1
	assert type(data.get('count')) == int and data['count'] > 0
	assert data.get('ingredients')
	assert (data.get('type'),len(data['ingredients'])) in workstations

	ingredients = []

	for item,i in zip(data['ingredients'],range(999)):
		if type(item) == str:
			if item == "":
				continue
			ingredients.append(f"{{Slot:{i}b,Count:1b,{crafting_items[item]}}}")
			continue
		assert type(item) == dict # ingredient must be a type of STRING or {"id":STRING,"count":INT}
		assert type(item.get('id')) == str and type(item.get('count')) == int
		ingredients.append(f"{{Slot:{i}b,Count:{item['count']}b,{crafting_items[item['id']]}}}")

	if data.get('nbt') and data['nbt'][0] == '{' and data['nbt'][-1] == '}':
		data['nbt'] = data['nbt'][1:-1]

	ingredients = ','.join(ingredients)

	print(f"execute if block ~ ~ ~ minecraft:dropper{{Items:[{ingredients}]}} "
		f"run data merge block ~ ~ ~ {{Items:[{{Slot:4b,Count:{data['count']}b,{crafting_items[output]},{data.get('nbt','')}}}]}}")
