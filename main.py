#!/bin/env python3
import json
import os

namespace = 'skymagic'

atlas_namespaces = {
	"minecraft" : ["mcitem",json.load(open('atlas-mapping-vanilla.json'))],
	"skymagic" :  ["smitem",json.load(open('atlas-mapping-skymagic.json'))]
}

workstations = [
	('magic_table',9),
	('crafting',9)
]

display_names = {}
crafting_items = {}
final_items = {}
crafting_recipes = {}
warnings = []

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


for item in json.load(open('vanila_items.json')):
	display_names["minecraft:"+item['name']] = item['displayName']

for item in display_names.keys():
	crafting_items[f'minecraft:{item.removeprefix("minecraft:")}'] = f'id: "minecraft:{item.removeprefix("minecraft:")}"'


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

def gen_display_name(item_name):
	return ' '.join([word[0].upper()+word[1::] for word in item_name.split('_')])

def gen_nbt(item,data):
	nbt = []
	nbt.append('display:{"Name":"{\\"text\\":\\"'+gen_display_name(item)+'\\",\\"italic\\":false}"}')
	# nbt.append(f'Tags:["{gen_display_name(item)}"]')
	if data.get('CustomModelData'):
		nbt.append(f'CustomModelData:{data.get("CustomModelData")}')
	# nbt.append("Enchantments:[]")
	nbt.append(data.get("nbt",""))

	return ','.join(nbt).removesuffix(',')

def html_item_icon(id,count=1,name=None):

	if type(id) == dict:
		count = id.get('count',1)
		id = id.get('id',"minecraft:null")
	assert type(id) == str

	if count == 1:
		count = "&nbsp"
	if id == "":
		id = "minecraft:air"


	item_namespace, id = id.split(":",1)
	fandom_minecraft_wiki_link = "https://minecraft.fandom.com/wiki/"
	base_html = f'<span id="item" title="{display_names.get(item_namespace+":"+id)}" class="item {atlas_namespaces[item_namespace][0]}" style="background-position: -%spx -%spx;" >{count}</span>'

	if item_namespace == "minecraft":
		base_html = f'<a target="_blank" href="{fandom_minecraft_wiki_link}{id}">{base_html}</a>'
	index = atlas_namespaces[item_namespace][1].get(id,1) - 1
	return base_html % ( (index%32)*32, int(index/32)*32 )
	

def load_items():
	for item_fname in os.listdir('items'):
			if not item_fname.endswith('.json'): continue
			for item, data in json.load(open(f'items/{item_fname}')).items():
				check(item, data)
				display_name = gen_display_name(item)
				crafting_items[f"{namespace}:{item}"] = f'id:"minecraft:{data["id"]}",tag:{{Tags:["{display_name}"]}}'
				final_items[f"{namespace}:{item}"] = f'id:"minecraft:{data["id"]}",tag:{{Tags:["{display_name}"],{gen_nbt(item,data)},%s }}'
				display_names[f"{namespace}:{item}"] = display_name


				display_names[f"{namespace}:{item}"] = display_name

				# print(gen_give_command(data['id'],gen_nbt(item,data)))
				# print(f"{namespace}:{item}{{{gen_nbt(item,data)}}}")

	for warn in warnings:
		print(f"\033[31mWARN: {warn}\033[39m")

# if warnings:
# 	exit(2)



def load_craftings(wiki):
	print()
	wiki.write(wiki_html)
	for crafting_fname in os.listdir('craftings'):
			if not crafting_fname.endswith('.json'): continue
			for output, data in json.load(open(f'craftings/{crafting_fname}')).items():
					if output.startswith("_"):
						continue
					assert type(data.get('ingredients')) == list
					if any([type(x) == list for x in data['ingredients']]):
							assert all([type(x) == list for x in data['ingredients']])
							craftings = data['ingredients']
 
					else:
							craftings = [data['ingredients']]
 
					# wiki.write(f'<span id="item-{output}">{display_names[output]}</span><br>')
					for crafting,is_last_crafting in zip(craftings,([False]*(len(craftings)-1))+[True]):
						data['ingredients'] = crafting


						if data.get('count') is None:
							data['count'] = 1
						assert type(data.get('count')) == int and data['count'] > 0
						assert data.get('ingredients')
						assert (data.get('type'),len(data['ingredients'])) in workstations

						ingredients = []

						wiki.write(data.get("wiki_name",display_names[output])+"<br>")

						for item,i in zip(data['ingredients'],range(999)):
							wiki.write(html_item_icon(item))
							if i == 5:
								wiki.write(" => "+html_item_icon(output,count=data.get('count',1)))
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
							if item.get('count') is None:
								item['count'] = 1
							assert type(item.get('id')) == str and type(item.get('count')) == int
							ingredients.append(f"{{Slot:{i}b,Count:{item['count']}b,{crafting_items[item['id']]}}}")


						if data.get('nbt') and data['nbt'][0] == '{' and data['nbt'][-1] == '}':
							data['nbt'] = data['nbt'][1:-1]

						ingredients = ','.join(ingredients)

						item_nbt = final_items.get(output,f'id:"{output}",%s') % data.get('nbt','')

						print(f"execute if block ~ ~ ~ minecraft:dropper{{Items:[{ingredients}]}} "
							f"run data merge block ~ ~ ~ {{Items:[{{Slot:4b,Count:{data['count']}b,{item_nbt}}}]}}")

def gen_wiki():
	with open('wiki.html','w') as wiki:
		load_craftings(wiki)

if __name__ == "__main__":
	load_items()
	# load_craftings()
	gen_wiki()
