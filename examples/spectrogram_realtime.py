# -*- coding: utf-8 -*-
import sys
import pyaudio
import numpy as np
from Queue import Queue
import time
import threading

from traits.api import *
from traitsui.api import *
from pyface.timer.api import Timer
from matplotlib import cm
from matplotlib.figure import Figure
from scpy2.traits.mpl_figure_editor import MPLFigureEditor

NUM_SAMPLES = 1024
SAMPLING_RATE = 8000
SPECTROGRAM_LENGTH = 100
NUM_LINES = 5


class DemoHandler(Handler):
    def closed(self, info, is_ok):
        info.object.timer.Stop()
        info.object.finish_event.set()
        info.object.thread.join()        
        return


class Demo(HasTraits):
    figure = Instance(Figure, ())
    timer = Instance(Timer)
    hifreq = Range(0, SAMPLING_RATE/2, SAMPLING_RATE/2)
    spectrum_list = List
    buffer_size = Int

    traits_view = View(
        VGroup(
            HGroup(
                Item('buffer_size', style="readonly"), 
                Item('hifreq')
            ),
            Item("figure", editor=MPLFigureEditor(toolbar=True), 
                 show_label=False),
            orientation = "vertical"),
        resizable=True, title="Audio Spectrum",
        width=900, height=500,
        handler=DemoHandler
    )

    def __init__(self, **traits):
        super(Demo, self).__init__(**traits)
        self._create_plot_component()
        self.queue = Queue()
        self.finish_event = threading.Event()        
        self.thread = threading.Thread(target=self.get_audio_data)
        self.thread.start()
        self.timer = Timer(10, self.on_timer)
        self.win_func = np.hanning(NUM_SAMPLES+1)[:NUM_SAMPLES]
        
    def _hifreq_changed(self):
        self.ax1.set_ylim(0, self.hifreq)
        
    def _create_plot_component(self):
        self.ax1 = self.figure.add_subplot(311)
        self.ax2 = self.figure.add_subplot(312)
        self.ax3 = self.figure.add_subplot(313)
        self.figure.subplots_adjust(bottom=0.05, top=0.95, left=0.05, right=0.95)
        
        self.spectrogram_data = np.full((NUM_SAMPLES/2, SPECTROGRAM_LENGTH), -90)
        
        x2 = float(SPECTROGRAM_LENGTH*NUM_SAMPLES)/float(SAMPLING_RATE)
        y2 = SAMPLING_RATE/2.0
        self.image_spectrogram = self.ax1.imshow(self.spectrogram_data, 
                        aspect="auto", vmin=-90, vmax=0, origin = "lower",
                        extent=[0, x2, 0, y2])
        
        self.frequency = np.linspace(0., y2, num=NUM_SAMPLES/2)
        self.time = np.linspace(0., float(NUM_SAMPLES)/SAMPLING_RATE, 
                                num=NUM_SAMPLES, endpoint=False)
        for i in xrange(NUM_LINES):
            self.ax2.plot(self.frequency, np.zeros_like(self.frequency), 
                          color=cm.Blues(float(i+1)/(NUM_LINES+1)))
            
        self.line_wave, = self.ax3.plot(self.time, np.zeros_like(self.time))
        self.ax3.set_ylim(-1, 1)
        self.ax3.set_xlim(0, self.time[-1])
        
    def on_timer(self, *args):
        self.buffer_size = self.queue.qsize()
        if self.buffer_size > 1:
            spectrum, wave = self.queue.get(False)
            self.spectrum_list.append(spectrum)
            if len(self.spectrum_list) > NUM_LINES: del self.spectrum_list[0]
            for i, data in enumerate(self.spectrum_list):
                self.ax2.lines[i].set_ydata(data)
            self.ax2.relim()
            self.ax2.autoscale_view()
            self.line_wave.set_ydata(wave)
                    
            self.spectrogram_data[:,:-1] = self.spectrogram_data[:,1:]
            self.spectrogram_data[:,-1] = spectrum
            self.image_spectrogram.set_data(self.spectrogram_data)
            
        self.figure.canvas.draw()

    def get_audio_data(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1,
                          rate=SAMPLING_RATE,
                          input=True, frames_per_buffer=NUM_SAMPLES)
        
        while not self.finish_event.is_set():
            audio_data  = np.fromstring(stream.read(NUM_SAMPLES), dtype=np.short)
            normalized_data = (audio_data / 32768.0)
            windowed_data = normalized_data * self.win_func
            fft_data = np.abs(np.fft.rfft(windowed_data))[:NUM_SAMPLES/2]
            fft_data /= NUM_SAMPLES
            np.log10(fft_data, fft_data)
            fft_data *= 20
            self.queue.put( (fft_data, normalized_data) )
            
        stream.close()
      

if __name__ == "__main__":
    demo = Demo()
    demo.configure_traits()