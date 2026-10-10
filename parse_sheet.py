import csv, json, datetime, re, sys
rows = list(csv.reader(open(sys.argv[1] if len(sys.argv)>1 else '/workspace/sheet.csv', encoding='utf-8')))
NAME_FIX = {'Mu Yi':'Muyi'}
DAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
week_start = datetime.date(2026,8,2)
assert week_start.weekday()==6
tasks, delivery, notes, people, warnings = {}, {}, {}, [], []
cur = None
def clean(s):
    s = s.replace('\r','')
    lines = [l.strip() for l in s.split('\n')]
    return '\n'.join(l for l in lines if l).strip()
for i,r in enumerate(rows):
    r = r + ['']*(15-len(r))
    if r[0].strip() in ('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC') and r[1].startswith('Sun'):
        cur = week_start if cur is None else cur + datetime.timedelta(days=7)
        for k in range(7):
            d = cur + datetime.timedelta(days=k)
            m = re.match(r'(\w+)\s+(\d+)', r[1+k].strip())
            if not m or m.group(1)!=DAYS[k] or int(m.group(2))!=d.day:
                warnings.append(f'row {i+1}: header {r[1+k]!r} != {d}')
        continue
    if cur is None: continue
    name = r[0].strip()
    if not name: continue
    name = NAME_FIX.get(name, name)
    is_deliv = '交付' in name or 'Delivery' in name
    has = any(clean(c) for c in r[1:])
    if not is_deliv and name not in people and has: people.append(name)
    for k in range(7):
        v = clean(r[1+k])
        if not v: continue
        ds = (cur + datetime.timedelta(days=k)).isoformat()
        if is_deliv: delivery[ds] = v
        else: tasks.setdefault(ds, {})[name] = v
    extra = [clean(c) for c in r[8:] if clean(c)]
    if extra:
        notes.setdefault(cur.isoformat(), {})['Delivery' if is_deliv else name] = ' | '.join(extra)
out = {'source':'Google Sheet 1h1vb6SfBvgyA0Ye8kFTKp7JjxrlGsDoG gid 423849879','parsedAt':datetime.datetime.now().isoformat(timespec='seconds'),
       'people':people,'tasks':tasks,'delivery':delivery,'weekNotes':notes}
json.dump(out, open('/workspace/team-schedule/seed.json','w'), ensure_ascii=False, indent=0)
print('people',people); print('days',len(tasks),'deliv',len(delivery)); print('notes',json.dumps(notes,ensure_ascii=False)); print('warnings',warnings)
print(tasks['2026-08-03'])
