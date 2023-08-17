#!/bin/env python3

namespace = 'skymagic'

import json

vanilla_items = {}

for item in json.load(open('vanila_items.json')):
	vanilla_items[item['name']] = item['displayName']

crafting_items = {}
for item in vanilla_items.keys():
	crafting_items[f'minecraft:{item}'] = f'id: "minecraft:{item}"'

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



for item, data in json.load(open(f'items/skymagic.json')).items():
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

wiki_html = '''
<style type="text/css">
	.mcitem{
		background-image:url(vanilla_atlas.png);
		width: 32px;
		height: 32px;
		display: inline-flex;
	}
</style>

'''

vanilla_mapping = json.load(open('atlas-mapping.json'))

print()
with open('wiki.html','w') as wiki:
	wiki.write(wiki_html)
	for output, data in json.load(open(f'craftings/skymagic.json')).items():
		if data.get('count') is None:
			data['count'] = 1
		assert type(data.get('count')) == int and data['count'] > 0
		assert data.get('ingredients')
		assert (data.get('type'),len(data['ingredients'])) in workstations

		ingredients = []

		for item,i in zip(data['ingredients'],range(999)):

			if type(item) == str:
				if item == "":
					index = vanilla_mapping.get("air",1) - 1
				else:
					index = vanilla_mapping.get(item.removeprefix("minecraft:"),1) - 1
			elif type(item) == dict:
				index = vanilla_mapping.get(item['id'].removeprefix("minecraft:"),1) - 1

			wiki.write(f'<span id="item" class="mcitem" style="background-position: -{(index%32)*32}px -{int(index/32)*32}px;" ></span>')
			if i == 5:
				wiki.write(" => ")
				index = vanilla_mapping.get(output.removeprefix("minecraft:"),1) - 1
				wiki.write(f'<span id="item" class="mcitem" style="background-position: -{(index%32)*32}px -{int(index/32)*32}px;" ></span>')
			if (i+1)%3 == 0:
				wiki.write("<br>\n")
			if i == 8:
				wiki.write("<br><br><br>\n")

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

		# print(f"execute if block ~ ~ ~ minecraft:dropper{{Items:[{ingredients}]}} "
		# 	f"run data merge block ~ ~ ~ {{Items:[{{Slot:4b,Count:{data['count']}b,{crafting_items[output]},{data.get('nbt','')}}}]}}")



