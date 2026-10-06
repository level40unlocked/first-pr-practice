"""Downloads the EP.4 voice lines: jobs_pending.txt (idx jobid) + per-index anchor timestamps (the URL timestamp is the creation second, +-3 s)."""
import subprocess, os, json
from datetime import datetime, timedelta
ANCH=[(1,10,"055702"),(11,20,"055713"),(21,30,"055724"),(31,35,"055735"),(38,40,"055735"),(36,37,"055752"),(41,46,"055753"),(47,56,"055803"),(57,66,"055813"),
(67,72,"055829"),(74,76,"055829"),(73,73,"055839"),(77,85,"055839"),(86,88,"055853"),(90,90,"055853"),(101,105,"055853"),(89,89,"055904"),(107,108,"055904"),(109,114,"055903"),
(106,106,"055919"),(115,123,"055919"),(124,129,"055930"),(131,133,"055930"),(130,130,"055946"),(134,142,"055946"),(143,152,"055956"),(153,153,"060012"),(155,155,"060012"),
(157,162,"060012"),(154,154,"060020"),(156,156,"060020")]
anchor={}
for a,b,t in ANCH:
    for i in range(a,b+1): anchor[i]=t
jobs={int(l.split()[0]):l.split()[1] for l in open("jobs_pending.txt")}
out={}
for i,j in sorted(jobs.items()):
    f=f"v1/ep04_{i:03d}.mp3"; ok=False
    base=datetime.strptime("20261006"+anchor[i],"%Y%m%d%H%M%S")
    for d in (0,1,-1,2,-2,3,-3):
        t=(base+timedelta(seconds=d)).strftime("%Y%m%d_%H%M%S")
        url=f"https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_{t}_{j}.mp3"
        r=subprocess.run(["curl","-sS","-f","-o",f,url],capture_output=True)
        if r.returncode==0 and os.path.getsize(f)>2000: out[str(i)]={"job":j,"url":url}; ok=True; break
    if not ok: print("FAILED",i)
json.dump(out,open("jobs_v1.json","w"),indent=1); print(len(out),"downloaded")
