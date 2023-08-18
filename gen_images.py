from main import check
from PIL import Image
import json
from math import ceil

textures_json = {}

txt_path = 'Sky_magic_TexturePack/assets/minecraft/models/item/%s.json'
png_path = 'Sky_magic_TexturePack/assets/{}/textures/{}.png'

for item, data in json.load(open(f'items/skymagic.json')).items():
	check(item,data)

	if not data.get('CustomModelData'):
		continue
	if not textures_json.get(txt_path % data["id"]):
		textures_json[txt_path % data["id"]] = {}
	textures_json[txt_path % data["id"]][data['CustomModelData']] = item

# print(textures_json)

txt_item_path = {}

for path, txts in textures_json.items():
	for override in json.load(open(path)).get("overrides",{}):
		t = txts.get(override.get('predicate',{}).get('custom_model_data'))
		if t is not None:
			txt_item_path[t] = override['model']

# print(txt_item_path)

icons = []

for item_id, image_path in txt_item_path.items():
	if image_path.count(":") == 0:
		image_path = f"minecraft:{image_path}"

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