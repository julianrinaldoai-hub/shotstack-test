import librosa, numpy as np, sys
y,sr=librosa.load(sys.argv[1],sr=22050,mono=True)
print("duration",len(y)/sr)
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,units='time')
print("tempo",tempo)
bt=np.array(beats); ib=np.diff(bt); print("beats",len(bt),"median IBI",np.median(ib),"first beats",np.round(bt[:12],3))
oenv=librosa.onset.onset_strength(y=y,sr=sr)
t=librosa.times_like(oenv,sr=sr)
rms=librosa.feature.rms(y=y)[0]; tr=librosa.times_like(rms,sr=sr)
# low-band energy (kick)
S=np.abs(librosa.stft(y)); f=librosa.fft_frequencies(sr=sr)
low=S[(f<150)].sum(0); lowdb=librosa.amplitude_to_db(low,ref=low.max())
print("\nRMS dB per 2s window:")
for a in np.arange(0,136,2):
    m=(tr>=a)&(tr<a+2); 
    lm=(t>=a)&(t<a+2)
    print(f"{a:5.0f}s rms={20*np.log10(rms[m].mean()+1e-9):6.1f}dB low={lowdb[lm].mean():6.1f} onset={oenv[lm].mean():4.2f}")
np.save(sys.argv[2]+"/beats.npy",bt)
# section boundaries via recurrence/agglomerative on chroma+mfcc
C=librosa.feature.chroma_cqt(y=y,sr=sr); M=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=13)
X=np.vstack([librosa.util.normalize(C),librosa.util.normalize(M)])
bf=librosa.time_to_frames(bt,sr=sr)
Xs=librosa.util.sync(X,bf)
for k in (6,8):
    b=librosa.segment.agglomerative(Xs,k)
    bts=librosa.frames_to_time(librosa.util.fix_frames(bf)[b],sr=sr)
    print(f"sections k={k}:",np.round(bts,2))
