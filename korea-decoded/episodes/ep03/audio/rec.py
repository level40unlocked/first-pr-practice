import json,sys,os,subprocess
# usage: rec.py <ts like 20261003_082532> idx:jobid idx:jobid ...  -> downloads v1/ep03_NN.mp3
ts=sys.argv[1]; p="jobs_v1.json"
cur=json.load(open(p)) if os.path.exists(p) else {}
for a in sys.argv[2:]:
    i,j=a.split(":"); url=f"https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_{ts}_{j}.mp3"
    cur[i]={"job":j,"url":url}
    f=f"v1/ep03_{int(i):02d}.mp3"
    from datetime import datetime,timedelta
    base=datetime.strptime(ts,"%Y%m%d_%H%M%S"); ok=False
    for d in (0,-1,1,-2,2,-3,3,-4,4,-5,5):
        t2=(base+timedelta(seconds=d)).strftime("%Y%m%d_%H%M%S")
        url=f"https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_{t2}_{j}.mp3"
        r=subprocess.run(["curl","-sS","-f","-o",f,url],capture_output=True)
        if r.returncode==0 and os.path.getsize(f)>2000: cur[i]={"job":j,"url":url}; ok=True; break
    if not ok: print("FAILED",i)
json.dump(cur,open(p,"w"),indent=1); print(len(cur),"recorded")
