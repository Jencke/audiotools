import audiotools.wav as wav
import audiotools as audio
import numpy as np
import numpy.testing as testing

import pytest
import matplotlib.pyplot as plt

plt.ioff()

def test_writewav_readwav():
    """Test invertability of readfile and writefile"""
    fs = 48000
    signal = audio.Signal(2, 2, fs)
    signal[:] = np.linspace(-1, 1, signal.n_samples)[:, None]

    wav.writefile("test.wav", signal, signal.fs)
    out, fs = wav.readfile("test.wav")
    testing.assert_allclose(out, signal)
