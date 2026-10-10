import json, pathlib
d = pathlib.Path('/workspace/team-schedule')
seed = json.loads((d/'seed.json').read_text())
js = json.dumps(seed, ensure_ascii=False, separators=(',',':')).replace('</','<\\/')
(d/'index.html').write_text((d/'template.html').read_text().replace('/*SEED_JSON*/null', js))
print('ok', (d/'index.html').stat().st_size)
