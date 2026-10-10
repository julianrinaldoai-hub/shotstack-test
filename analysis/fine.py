import librosa, numpy as np, sys
y,sr=librosa.load(sys.argv[1],sr=44100,mono=True,duration=40)
hop=128
env=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
t=librosa.times_like(env,sr=sr,hop_length=hop)
rms=librosa.feature.rms(y=y,hop_length=hop)[0]
print("rms 0-1.2s dB:",np.round(20*np.log10(rms[t<1.2].mean()),1))
for c in (1.149,9.33,17.485,31.75,32.229,33.762):
    m=(t>c-0.12)&(t<c+0.12); i=np.argmax(env[m]); print(f"near {c}: onset peak {t[m][i]:.3f}s")
# global tempo fit: onsets aligned to grid
on=librosa.onset.onset_detect(onset_envelope=env,sr=sr,hop_length=hop,units='time')
best=None
for bpm in np.arange(117.0,118.2,0.01):
    p=60/bpm
    for ph in np.arange(0,p,0.005):
        d=np.abs(((on-ph+p/2)%p)-p/2); s=np.exp(-(d/0.02)**2).sum()
        if best is None or s>best[0]: best=(s,bpm,ph)
print("grid fit bpm=%.2f phase=%.3f"%(best[1],best[2]))
p=60/best[1]; ph=best[2]
k=np.round((1.149-ph)/p); first=ph+k*p
print("downbeat grid from %.3f: bars ->"%first, np.round(first+np.arange(0,17)*4*p,3))
