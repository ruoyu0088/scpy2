# -*- coding: utf-8 -*-
import numpy as np
import wave

class FrequencyProcess(object):
    def __init__(self, infile, outfile, fft_size): #{1}
        self.fft_size = fft_size
        
        if type(infile) == str:
            f = wave.open(infile, "rb")
            nchannels, sampwidth, framerate, nframes, _, _ = f.getparams()
            if nchannels != 1:
                print "only support one channel wave file"
            self.framerate = framerate
            
            self.input = np.fromstring(f.readframes(nframes), dtype=np.short)
            f.close()
        else:
            self.input = infile
            self.framerate = 44100
        
        self.result = self.process()
        
        f = wave.open(outfile, "wb")
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(self.framerate)
        f.writeframes(self.result.astype(np.short).tostring())
        f.close()
        
    def process_init(self):
        "频域信号处理的初始化"
        pass
        
    def process_block(self, block):
        "对频域信号块block进行处理，并返回"
        return block
        
    def process(self):
        self.process_init() #{2}
        out = np.zeros(len(self.input))
        window = np.hanning(self.fft_size)
        
        start = 0
        while start + self.fft_size < len(self.input):
            block_time = self.input[start:start+self.fft_size]
            block_freq = np.fft.rfft(block_time)
            block_freq = self.process_block(block_freq)  #{3}       
            block_time = np.fft.irfft(block_freq)
            out[start:start+self.fft_size] += block_time * window # hanning窗
            start += self.fft_size//2
        
        return out