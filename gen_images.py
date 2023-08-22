
#!/bin/python3
from main import check
from PIL import Image
from math import ceil
import json
import os

textures_json = {}

txt_path = 'Sky_magic_TexturePack/assets/minecraft/models/item/%s.json'
model_path = 'Sky_magic_TexturePack/assets/{}/models/{}.json'
png_path = 'Sky_magic_TexturePack/assets/{}/textures/{}.png'


for fname in os.listdir('items'):
	for item, data in json.load(open(f'items/{fname}')).items():
		check(item,data)

		data['id'] = data['id'].removeprefix("minecraft:")

		if not data.get('CustomModelData'):
			continue
		if not textures_json.get(data["id"]):
			textures_json[data["id"]] = {}
		textures_json[data["id"]][data['CustomModelData']] = item

txt_item_path = {}

print(textures_json)

for item_id, txts in textures_json.items():
	try:
		for override in json.load(open(txt_path % item_id)).get("overrides",{}):
			t = txts.get(override.get('predicate',{}).get('custom_model_data'))
			if t is not None:
				txt_item_path[t] = override['model'].removeprefix('minecraft:') # if minecraft namespace, use vanilla txt. if non use from txt, its not perfekt but works
	except FileNotFoundError:
		for t in txts.values():
			txt_item_path[t] = f"minecraft:item/{item_id}"

print(txt_item_path)

icons = []

vanilla_atlas_mapping = json.load(open('atlas-mapping-vanilla.json'))
vanilla_atlas = Image.open('vanilla_atlas.png')


for item_id, image_path in txt_item_path.items():

	if image_path.startswith('minecraft:'):
		idx = vanilla_atlas_mapping.get(image_path.removeprefix('minecraft:item/'))-1
		x,y = (idx%32)*32, int(idx/32)*32
		i = vanilla_atlas.crop(box=(x,y,x+32,y+32))
		i = i.resize((16,16), resample=Image.NEAREST)
	else:
		if image_path.count(":") == 0:
			image_path = f"minecraft:{image_path}"
		print(model_path.format(*image_path.split(":",1)))
		i = Image.open(png_path.format(*image_path.split(":",1)))
	icons.append((item_id,i))

row_num = ceil(len(icons)/32)

atlas = Image.new('RGBA',(1024,row_num*32),(0,0,0,0))
for i,idx in zip(icons,range(1,len(icons)+1)): # i'm countig from 1 not form 0 like minecraft wiki atlases
	item_id, i = i
	i = i.crop(box=(0,0,16,16))
	i = i.resize((32,32), resample=Image.NEAREST)
	atlas.paste(i,box=((idx%32)*32, int(idx/32)*32))
	i.close()

v = Image.open("vanilla_atlas.png")
atlas.paste(v.crop(box=(0,0,32,32)),box=(0,0))
v.close()
atlas.save("skymagic_atlas.png")
atlas.close()

with open('atlas-mapping-skymagic.json','w') as f:
	o = {}
	for x in (zip(icons,range(1,len(icons)+1))):
		o[x[0][0]]=x[1]+1
	f.write(json.dumps(o))