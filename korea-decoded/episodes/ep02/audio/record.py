import json,sys,os
# usage: record.py '<json list of {index,job_id,result_url}>'
p="jobs.json"
cur=json.load(open(p)) if os.path.exists(p) else {}
for j in json.loads(sys.argv[1]): cur[str(j["index"])]={"job":j["job_id"],"url":j["result_url"]}
json.dump(cur,open(p,"w"),indent=1); print(len(cur),"recorded")
