# -*- coding: utf-8 -*-
import numpy as np
from scipy.interpolate import UnivariateSpline
from spectrum_freq_process import FrequencyProcess

class FrequencyFilter(FrequencyProcess):
    def __init__(self, infile, outfile, fft_size, parameters): #{1}
        self.parameters = parameters
        super(FrequencyFilter, self).__init__(infile, outfile, fft_size)
        
    def process_init(self):
        self.freqs = np.arange(0, self.fft_size//2+1, 1.0)
        freq_points = []
        freq_gains = []
        for freq, gain in self.parameters:
            # 实际频率转换为frequency bin
            freq_points.append(float(freq) / self.framerate * self.fft_size)
            freq_gains.append( 10**(gain/20.0) ) # dB转换为乘积系数
        gain_func = UnivariateSpline(freq_points, freq_gains, k=1, s=0) #{2}
        self.gain = gain_func(self.freqs)
        
    def process_block(self, block):
        return block * self.gain #{3}
        
if __name__ == "__main__":
    from scipy import signal
    t = np.arange(0, 10, 1/44100.0)
    sweep = signal.chirp(t, f0=100, t1 = 10, f1=4000) * 10000
    filter_settings = [(0,0),(200, 0),(400, -20),(1000, -20),
        (1500, 0),(3000, 0),(3500, -20),(30000, -20)]
    FrequencyFilter(sweep, "chrip_filter.wav", 1024, filter_settings)
    FrequencyFilter("voice.wav", "voice_filter.wav", 1024, filter_settings)