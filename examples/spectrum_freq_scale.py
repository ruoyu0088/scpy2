# -*- coding: utf-8 -*-
import numpy as np
from spectrum_freq_process import FrequencyProcess
from scipy.interpolate import UnivariateSpline

class FrequencyScale(FrequencyProcess):
    def __init__(self, infile, outfile, fft_size, scale):
        self.scale = scale        
        super(FrequencyScale, self).__init__(infile, outfile, fft_size)
        
    def process_init(self):
        self.freqs = np.arange(0, self.fft_size//2+1, 1.0)
        self.phases = np.zeros_like(self.freqs)
        self.last_phases = np.zeros_like(self.freqs)
        
    def process_block(self, block):
        new_freqs = self.freqs * self.scale
        amp = np.abs(block)
        phases = np.angle(block)
        self.phases += (phases - self.last_phases) * self.scale
        self.last_phases = phases
        amp_new = UnivariateSpline(new_freqs, amp, k=3, s=0)(self.freqs)
        block = amp_new * np.exp(self.phases * 1j)
        block[int(np.max(new_freqs)):] = 0
        return block
        
if __name__ == "__main__":
    FrequencyScale("voice.wav", "voice_fscale.wav", 4096, 1.1)
