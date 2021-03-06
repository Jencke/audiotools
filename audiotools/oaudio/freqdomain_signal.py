import numpy as np
import audiotools as audio
from copy import deepcopy

from .base_signal import BaseSignal

class FrequencyDomainSignal(BaseSignal):

    def __new__(cls, n_channels, duration, fs, dtype=complex):
        obj = BaseSignal.__new__(cls, n_channels, duration, fs, dtype)
        return obj

    @property
    def freq(self):
        r"""Returns the frequency axis

        Returns
        -------
        The frequency axis in Hz : numpy.ndarray

        """
        freq = np.fft.fftfreq(self.n_samples, 1. / self.fs)
        return freq

    @property
    def omega(self):
        r"""Returns the angular frequency axis

        Returns
        -------
        The angular frequencies : numpy.ndarray

        """
        return self.freq * 2 * np.pi

    @property
    def phase(self):
        r"""The Argument of the frequency components

        Returns
        -------
        The arguments in radiants : numpy.ndarray

        """
        return np.angle(self)
    angle = phase

    @property
    def mag(self):
        r"""Retruns the magnitudes of the frequency components

        equivalent to :meth:`audiotools.FrequencyDomainSignal.abs()`

        Returns
        -------
        The magnitudes : numpy.ndarray
        """
        return self.abs()

    def time_shift(self, time):
        r"""Apply a time shift

        Time shift the signal by a linear phase shift by
        multiplying all frequency components with:

        .. math:: H(\omega) = e^{-j\omega\Delta t}

        where :math:`j` is the complex unit, :math:`omega` the
        circular frequency and :math:`\Delta t` the timeshift.

        Parameters
        ----------
        time : scalar
            The time by which the signal should be shifted

        Returns
        -------
        Returns itself : FrequencyDomainSignal

        Also See
        --------
        audiotools.Signal.delay

        """

        phases = - self.omega * time

        # fix the last bin in case of odd samples in order to keep the
        # tranformed signal real
        if not self.n_samples % 2:
            phases[self.n_samples//2] = 0

        self *= np.exp(1j * phases)
        return self

    def phase_shift(self, phase):
        r"""Apply a phase shift

        Phase shift the spectrum by multiplying all frequency
        components with:

        .. math:: H(\omega) = e^{-j\psi}

        where :math:`j` is the complex unit and :math:`\psi` is the
        desired phaseshift.

        Parameters
        ----------
        phase : scalar
            The phaseshift

        Returns
        -------
        Returns itself : FrequencyDomainSignal

        Also See
        --------
        audiotools.Signal.phase_shift

        """

        shift_val = - 1.0j * phase * np.sign(self.freq)
        self *= np.exp(shift_val)
        return self


    def from_timedomain(self, signal):
        self[:] = np.fft.fft(signal, axis=0)
        self /= signal.n_samples
        return self

    def to_timedomain(self):
        """Convert to timedomain.

        Convert to timedomain by means of inverse DFT. If the complex
        part after DFT is small (< 222e-16), it is neglected. This
        method is not applied in-place but a new
        :meth:'audiotools.Signal' object is returned

        Returns:
        --------
        Signal : The timedomain representation

        """

        # revert normalization
        self *= self.n_samples
        wv = np.fft.ifft(self, axis=0)
        wv = np.real_if_close(wv)
        signal = audio.Signal(self.n_channels, self.duration, self.fs)
        signal[:] = wv
        return signal

    def to_analytical(self):
        nsamp = self.n_samples

        h = np.zeros(nsamp)

        if nsamp % 2 == 0:
            h[0] = h[nsamp // 2] = 1
            h[1:nsamp // 2] = 2
        else:
            h[0] = 1
            h[1:(nsamp + 1) // 2] = 2

        if self.ndim > 1:
            ind = [np.newaxis] * self.ndim
            ind[0] = slice(None)
            h = h[tuple(ind)]

        signal = audio.AnalyticalSignal(self.n_channels, self.duration, self.fs,
                                        dtype=complex)
        signal[:] = np.fft.ifft(self.copy() * h * self.n_samples, axis=0)
        return signal
