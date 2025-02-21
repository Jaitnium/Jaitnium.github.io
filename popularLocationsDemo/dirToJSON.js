import os
import json

def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir\
(path)]
    else:
        d['type'] = "file"
    return d

outfile = "index.json"

with open(outfile, 'w') as outfile:
    json.dump(path_to_dict('mapData'), outfile, indent=4, sort_keys=True, separators=(',', ':'))
