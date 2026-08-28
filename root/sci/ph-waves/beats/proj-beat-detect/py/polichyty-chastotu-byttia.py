def beat_freq_fft(env, fs):
    """FFT обвідної: беремо найпотужніший бін, крім сталого."""
    e = env - env.mean()                 # прибрати DC, щоб не переміг бін 0
    spec  = np.abs(np.fft.rfft(e))
    freqs = np.fft.rfftfreq(len(e), 1/fs)
    spec[0] = 0
    return freqs[np.argmax(spec)]

print(beat_freq_fft(env_hil, fs))                       # -> 3.0
print(beat_freq_fft(envelope_rectify(x, fs), fs))       # -> 3.0
