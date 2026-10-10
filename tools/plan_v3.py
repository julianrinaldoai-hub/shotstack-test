FPS=24; BEAT=60/74.0; BAR=4*BEAT; PH=0.720
bs=lambda n: PH+(n-1)*BAR
f=lambda t: round(round(t*FPS)/FPS,4)
# music map: (track_start, track_end) segments -> video
SEG=[(bs(7),bs(13)),(bs(17),bs(19)),(bs(34),112.8)]
def vt(bar_no, beat=0):
    off=0
    for a,b in SEG:
        x=bs(bar_no)+beat*BEAT
        if a-1e-6<=x<b+1e-6: return f(off+x-a)
        off+=b-a
    raise ValueError(bar_no)
END=f(sum(b-a for a,b in SEG))
def avg(a,b,e): return {"lin":(a+b)/2,"in":a+(b-a)/3,"out":a+(b-a)*2/3}[e]
def used(L,prof):
    # prof: list of (t_start, t_len, from, to, ease); hold first 'from' before, last 'to' after
    if isinstance(prof,(int,float)): return prof*L
    t=0;u=0;cur=prof[0][2]
    for s,l,a,b,e in prof: u+=cur*(s-t)+avg(a,b,e)*l; t=s+l; cur=b
    return u+cur*(L-t)
shots=[]
def add(name,clip,start,end,trim,prof,role,sect):
    L=round(end-start,4); u=used(L,prof); shots.append((sect,name,clip,start,end,L,trim,trim+u,prof,role))
# BUILD
add("1","04",vt(7),vt(8),0.00,0.65,"opener: fire, window, kitchen; fade from black","BUILD")
add("2","02",vt(8),vt(9),0.00,[(1.40,1.84,0.9,1.6,"in")],"open plan; ACCEL into lift","BUILD")
# WAVE 1
add("3","07",vt(9),vt(10),0.00,[(0.0,1.3,1.4,0.6,"out")],"HERO 1 on lift: office + olive foreground, snap then settle","WAVE 1")
for i,(c,tr,role) in enumerate([("04",2.15,"stove + dining"),("05",0.10,"skylight, tilt down"),("06",0.15,"bathtub (camera right)"),("07",3.20,"desk + mountain window")]):
    add(f"4{'abcd'[i]}",c,vt(10,i),vt(10,i+1) if i<3 else vt(11),tr,1.0,role,"MONTAGE A")
add("5","08",vt(11),vt(12),0.00,[(1.60,1.64,0.7,1.5,"in")],"HERO 2: bedroom, lake + mountain window; ACCEL into montage","WAVE 1")
add("6a","02",vt(12,0),vt(12,1),3.40,0.75,"living + kitchen close","MONTAGE B")
add("6b","07",vt(12,1),vt(12,2),2.33,1.0,"olive tree leaving frame, desk","MONTAGE B")
add("6c","05",vt(12,2),vt(17),1.00,[(0.0,1.62,1.3,0.7,"out")],"attic push, BRAKES into the breakdown","MONTAGE B")
# BREAKDOWN
add("7","06",vt(17),vt(18),1.05,[(1.60,1.64,0.75,1.7,"in")],"bathtub, calm; ACCEL into lift 2","BREAKDOWN")
# WAVE 2 (lift 2)
for i,(c,tr,role) in enumerate([("08",2.80,"bed + lake window close"),("04",3.05,"candles + table close"),("05",3.10,"attic bed close")]):
    add(f"8{'abc'[i]}",c,vt(18,i),vt(18,i+1),tr,1.0,role,"MONTAGE C")
add("9","01",vt(18,3),END,0.00,[(0.0,1.8,1.4,0.55,"out")],"EXTERIOR landing: house + pool + mountains, pull-back; fade out","OUTRO")
src={}
print(f"{'sec':10s} {'#':3s} {'clip':4s} {'video in→out':>17s} {'len':>6s}  src in→out   speed")
for s in shots:
    sect,n,c,a,b,L,t0,t1,prof,role=s
    sp=prof if isinstance(prof,(int,float)) else " ; ".join(f"{fr}→{to}× over {l:.2f}s @{st:.2f}s ({e})" for st,l,fr,to,e in prof)
    print(f"{sect:10s} {n:3s} {c:4s} {a:7.3f}→{b:7.3f} {L:6.3f}  {t0:4.2f}→{t1:4.2f}  {sp}   | {role}")
    src.setdefault(c,[]).append((t0,t1,n))
print("\nEND",END)
print("\nper-clip source usage:")
for c in sorted(src):
    r=sorted(src[c]); ok=all(r[i][1]<=r[i+1][0]+1e-6 for i in range(len(r)-1)) and r[-1][1]<=4.0417
    print(f"  {c}: "+"  ".join(f"[{a:.2f}–{b:.2f}] #{n}" for a,b,n in r)+("" if ok else "   <-- OVERLAP/OVERRUN"))
print("\nkey video times: lift1",vt(9),"montageA",vt(10),"hero2",vt(11),"montageB",vt(12),"breakdown",vt(17),"lift2",vt(18),"outro bar34",vt(34))
