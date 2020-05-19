import numpy as np
import audiotools as audio
from audiotools.filter import brickwall, gammatone
import copy

class BaseSignal(np.ndarray):
    r"""
    Attributes:
    -----------
    waveform : ndarray
      The signals waveform
    fs
    n_channels
    n_samples
    duration
    time
    """

    def __new__(cls, n_channels, duration, fs, dtype=float):

        n_samples = audio.nsamples(duration, fs)

        if n_channels == 1:
            obj = super(C, cls).__new__(cls, shape=(n_samples),
                                        dtype=dtype)
        else:
            obj = super(C, cls).__new__(cls, shape=(n_samples, n_channels),
                                        dtype=dtype)
        obj._fs = fs
        obj.fill(0)
        return obj

    # setter and getter to handle the sample rates
    @property
    def fs(self):
        """Get the signals sampling rate"""

        return self._fs
    @fs.setter
    def fs(self, fs):
        """Set the signals sampling rate"""

        # If no fs provided or allready defined:
        if fs == None and self._fs == None:
            raise ValueError('No sampling rate provided')

        # If fs is defined
        elif fs != None:
            if self._fs == None:
                self._fs = fs
            elif self._fs != fs:
                raise ValueError('Sampling rate can\'t be changed')

    # setter and getter to handle the number of channels in the signal
    @property
    def n_channels(self):
        """Get the number of channels in the signal"""
        if self.ndim == 1:
            return 1
        else:
            return self.shape[1]

    @property
    def n_samples(self):
        """Get the number of samples in the signal"""
        return self.shape[0]

    @property
    def duration(self):
        """Get the duration of the signal in seconds"""
        duration = self.n_samples / self.fs

        return duration
