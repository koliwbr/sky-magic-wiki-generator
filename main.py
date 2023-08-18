#!/bin/env python3

namespace = 'skymagic'

import json

display_names = {}

for item in json.load(open('vanila_items.json')):
	display_names["minecraft:"+item['name']] = item['displayName']

crafting_items = {}
for item in display_names.keys():
	crafting_items[f'minecraft:{item.removeprefix("minecraft:")}'] = f'id: "minecraft:{item}"'

warnings = []

def check(item, data):
	assert type(data.get('id')) == str # check if ID exist, is string exist and is not empty
	item_id = data['id'].removeprefix('minecraft:')
	assert display_names.get("minecraft:"+item_id) # check if base item exist in minecraft

	if not data.get('CustomModelData'):
		try:
			warnings.append(f"{namespace}:{item} => No CustomModelData!")
		except NameError:
			pass

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

def html_item_icon(id,count=1):
	namespaces = {
		"minecraft" : ["mcitem",json.load(open('atlas-mapping-vanilla.json'))],
		"skymagic" :  ["smitem",json.load(open('atlas-mapping-skymagic.json'))]
	}

	if type(id) == dict:
		count = id.get('count',1)
		id = id.get('id',"minecraft:null")

	if count == 1:
		count = "&nbsp"
	if id == "":
		id = "minecraft:air"

	assert type(id) == str

	item_namespace, id = id.split(":",1)
	fandom_minecraft_wiki_link = "https://minecraft.fandom.com/wiki/"
	base_html = f'<span id="item" class="item {namespaces[item_namespace][0]}" style="background-position: -%spx -%spx;" >{count}</span>'

	if item_namespace == "minecraft":
		base_html = f'<a target="_blank" href="{fandom_minecraft_wiki_link}{id}">{base_html}</a>'
	index = namespaces[item_namespace][1].get(id,1) - 1
	return base_html % ( (index%32)*32, int(index/32)*32 )
	

def load_items():
	for item, data in json.load(open(f'items/skymagic.json')).items():
		check(item, data)
		display_name = get_display_name(item)
		crafting_items[f"{namespace}:{item}"] = f'id:"minecraft:{data["id"]}",tag:{{Tags:["{display_name}"]}}'
		display_names[f"{namespace}:{item}"] = display_name

		# print(gen_give_command(data['id'],gen_nbt(item,data)))
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
	}
	.smitem{
		background-image:url(skymagic_atlas.png);
	}
	.item{
		width: 32px;
		height: 32px;
		display: inline-flex;
	    background-color: lightgray;
	    margin: 2px;
	}
</style>
<script type="text/javascript" src="https://livejs.com/live.js"></script>
'''

def load_craftings():

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

			wiki.write(display_names[output]+"<br>")

			for item,i in zip(data['ingredients'],range(999)):
				wiki.write(html_item_icon(item))
				if i == 5:
					wiki.write(" => "+html_item_icon(output))
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


if __name__ == "__main__":
	load_items()
	load_craftings()