import sys, subprocess, numpy as np
W,H=368,200
def frames(p):
    raw=subprocess.run(["ffmpeg","-v","error","-i",p,"-map","0:v:0","-vf",f"scale={W}:{H},format=gray","-f","rawvideo","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,H,W).astype(np.float32)
def pc(a,b):
    win=np.outer(np.hanning(a.shape[0]),np.hanning(a.shape[1]))
    A=np.fft.fft2((a-a.mean())*win);B=np.fft.fft2((b-b.mean())*win)
    R=A*np.conj(B);R/=np.abs(R)+1e-9;r=np.fft.ifft2(R).real
    y,x=np.unravel_index(r.argmax(),r.shape)
    if y>a.shape[0]//2:y-=a.shape[0]
    if x>a.shape[1]//2:x-=a.shape[1]
    return x,y  # content shift from b to a
for p in sys.argv[1:]:
    F=frames(p); n=len(F); step=4
    rows=[]
    for i in range(0,n-step,step):
        a,b=F[i],F[i+step]
        h2,w2=H//2,W//2
        q={k:pc(b[s],a[s]) for k,s in {"tl":np.s_[:h2,:w2],"tr":np.s_[:h2,w2:],"bl":np.s_[h2:,:w2],"br":np.s_[h2:,w2:]}.items()}
        dx=np.mean([v[0] for v in q.values()]);dy=np.mean([v[1] for v in q.values()])
        div=((q["tr"][0]+q["br"][0])-(q["tl"][0]+q["bl"][0]))/2+((q["bl"][1]+q["br"][1])-(q["tl"][1]+q["tr"][1]))/2
        rows.append((i/24,dx,dy,div))
    R=np.array(rows)
    print(p.split('/')[-1], f"frames={n}")
    for seg in np.array_split(R,5):
        print(f"  t={seg[0,0]:.1f}-{seg[-1,0]+step/24:.1f}s  content dx={seg[:,1].mean():+5.1f}px  dy={seg[:,2].mean():+5.1f}px  divergence={seg[:,3].mean():+5.1f}  (per {step} frames @368w)")
