# pip install "nbtlib==1.12.1"

import nbtlib
from pprint import pprint
import json

tag = nbtlib.load('database_empty_entry.nbt')

print(json.dumps(tag))