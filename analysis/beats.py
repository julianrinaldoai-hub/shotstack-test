import librosa, numpy as np, sys
y,sr=librosa.load(sys.argv[1],sr=22050,mono=True,duration=40)
hop=256
S=np.abs(librosa.stft(y,hop_length=hop)); f=librosa.fft_frequencies(sr=sr)
t=librosa.frames_to_time(np.arange(S.shape[1]),sr=sr,hop_length=hop)
def flux(band):
    X=librosa.amplitude_to_db(S[band],ref=np.max); d=np.maximum(0,np.diff(X,axis=1)).mean(0); return np.concatenate([[0],d])
lowf=flux(f<120); midf=flux((f>1500)&(f<6000)); full=flux(f>0)
rms=librosa.feature.rms(y=y,hop_length=hop)[0]
# onset peaks
on=librosa.onset.onset_detect(onset_envelope=full,sr=sr,hop_length=hop,units='time',backtrack=False)
print("first onsets:",np.round(on[on<4],3))
bt=np.load(sys.argv[2])
bt=bt[bt<40]
print(" beat#  time   lowflux  hiflux  rmsdB")
for i,b in enumerate(bt):
    m=(t>=b-0.04)&(t<b+0.06)
    print(f"{i:4d} {b:7.3f}  {lowf[m].max():6.2f}  {midf[m].max():6.2f}  {20*np.log10(rms[m].mean()):6.1f}")
# bar phase: sum low flux by beat mod 4
L=np.array([lowf[(t>=b-0.04)&(t<b+0.06)].max() for b in bt])
for ph in range(4): print("phase",ph,"mean low",L[ph::4].mean().round(2))
