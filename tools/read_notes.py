import json, pathlib, sys
root=pathlib.Path(r'D:\gwl')
day=sys.argv[1]
lo=int(sys.argv[2]) if len(sys.argv)>2 else 0
hi=int(sys.argv[3]) if len(sys.argv)>3 else 99
for p in sorted((root/day/'tmp/pdfs').glob('notes*.json')):
    data=json.loads(p.read_text(encoding='utf-8'))
    if isinstance(data,dict):
        data=list(data.values())
    for n in data:
        if not lo<=n['id']<=hi: continue
        print('\n###',day,n['id'],n['title'])
        for k,v in n.items():
            if k in ['id','title']: continue
            if isinstance(v,list):
                print(k+':')
                for x in v: print(' | '.join(map(str,x)) if isinstance(x,list) else x)
            else: print(k+': '+str(v))
