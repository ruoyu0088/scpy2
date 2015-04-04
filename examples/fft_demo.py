# -*- coding: utf-8 -*-
from traits.api import (Str, Float, HasTraits, Range, Instance, 
                        on_trait_change, Enum)

from traitsui.api import Item, View, VGroup, HSplit, VSplit

import numpy as np

from matplotlib.figure import Figure

from scpy2.traits.mpl_figure_editor import MPLFigureEditor


# 取FFT计算的结果freqs中的前n项进行合成，返回合成结果，计算loops个周期的波形
def fft_combine(freqs, n, loops=1):
    length = len(freqs) * loops
    data = np.zeros(length)
    index = loops * np.arange(0, length, 1.0) / length * (2 * np.pi)
    for k, p in enumerate(freqs[:n]):
        if k != 0: p *= 2 # 除去直流成分之外，其余的系数都*2
        data += np.real(p) * np.cos(k*index) # 余弦成分的系数为实数部
        data -= np.imag(p) * np.sin(k*index) # 正弦成分的系数为负的虚数部
    return index, data
    

class BaseWave(HasTraits):
    
    def get_func(self):
        raise NotImplemented
    

class TriangleWave(BaseWave):
    # 指定三角波的最窄和最宽范围，由于Range类型不能将常数和Traits属性名混用
    # 所以定义这两个值不变的Trait属性
    low = Float(0.02)
    hi = Float(1.0)

    # 三角波形的宽度
    wave_width = Range("low", "hi", 0.5)

    # 三角波的顶点C的x轴坐标
    length_c = Range("low", "wave_width", 0.5)

    # 三角波的定点的y轴坐标
    height_c = Range(0.0, 2.0, 1.0)
    
    # 设置用户界面的视图， 注意一定要指定窗口的大小，这样绘图容器才能正常初始化
    view = View(
            VGroup(
                Item("wave_width", label=u"波形宽度"),
                Item("length_c", label=u"最高点x坐标"),
                Item("height_c", label=u"最高点y坐标"),
            ))

    # 返回一个ufunc计算指定参数的三角波
    def get_func(self):
        c = self.wave_width
        c0 = self.length_c
        hc = self.height_c

        def trifunc(x):
            x = x - int(x) # 三角波的周期为1，因此只取x坐标的小数部分进行计算
            if x >= c: r = 0.0
            elif x < c0: r = x / c0 * hc
            else: r = (c-x) / (c-c0) * hc
            return r

        # 用trifunc函数创建一个ufunc函数，可以直接对数组进行计算, 不过通过此函数
        # 计算得到的是一个Object数组，需要进行类型转换
        return np.frompyfunc(trifunc, 1, 1)
        

class RectangleWave(BaseWave):
    low = Range(0.0, 1.0, 0.1)
    hi = Range(0.0, 1.0, 0.5)
    height = Range(0, 2.0, 1.0)
    
    view = View(
            VGroup(
                Item("low", label=u"跳变X轴1"),
                Item("hi", label=u"跳变X轴2"),
                Item("height", label=u"高度"),
            ))

    # 返回一个ufunc计算指定参数的三角波
    def get_func(self):
        low = self.low
        hi = self.hi
        height = self.height

        def rectfunc(x):
            x = x - np.floor(x)
            r = np.zeros_like(x)
            if low < hi:
                r[(x > low) & (x < hi)] = height
            else:
                r[(x > low) | (x < hi)] = height
            return r

        return rectfunc
        

class FFTDemo(HasTraits):
    
    select = Enum([cls.__name__ for cls in BaseWave.__subclasses__()])
    wave = Instance(BaseWave)
    
    # FFT计算所使用的取样点数，这里用一个Enum类型的属性以供用户从列表中选择
    fftsize = Enum(256, [(2**x) for x in range(6, 12)])

    # 用于显示FFT的结果
    peak_list = Str
    # 采用多少个频率合成形
    N = Range(1, 40, 4)
    
    figure = Instance(Figure, ())
    
    view = View(
        HSplit(    
            VSplit(
                VGroup(
                    Item("select", label=u"波形类型"),
                    Item("wave", style="custom", label=u"波形属性"),
                    Item("fftsize", label=u"FFT点数"),
                    Item("N", label=u"合成波频率数"),
                    show_labels = True,    
                ),
                 Item("peak_list", style="custom", show_label=False, 
                      width=100, height=250)
            ),
            VGroup(
                Item("figure", editor=MPLFigureEditor(toolbar=True)),
                show_labels = False),
        ),
        title = u"FFT演示",
        resizable = True,
        width = 1280,
        height = 600,        
    )
    
    def __init__(self, **traits):
        super(FFTDemo, self).__init__(**traits)
        
        self.ax1 = self.figure.add_subplot(211)
        self.ax2 = self.figure.add_subplot(212)
        
        self.ax1.set_title("FFT")
        self.ax2.set_title("Wave")
        
        self.line_peaks, = self.ax1.plot([0], [0], "o")
        self.line_wave,  = self.ax2.plot([0], [0])
        self.line_wave2, = self.ax2.plot([0], [0])
        
        self._select_changed()
        
    def _select_changed(self):
        klass = globals()[self.select]
        self.wave = klass()
        
    @on_trait_change("wave, wave.[], fftsize")
    def draw(self):
        fftsize = self.fftsize
        x_data = np.arange(0, 1.0, 1.0/self.fftsize)
        func = self.wave.get_func()
        # 将func函数的返回值强制转换成float64
        y_data = func(x_data).astype(float)

        # 计算频谱
        fft_parameters = np.fft.fft(y_data) / len(y_data)
        self.fft_parameters = fft_parameters
        
        # 计算各个频率的振幅
        fft_data = np.clip(20*np.log10(np.abs(fft_parameters))[:fftsize/2+1], 
                           -120, 120)
        
        self.line_peaks.set_data(np.arange(0, len(fft_data)), fft_data) # x坐标为频率编号
        self.line_wave.set_data(np.arange(0, self.fftsize), y_data)
        
        # 合成波的x坐标为取样点，显示2个周期
        self.line_wave2.set_xdata(np.arange(0, 2*self.fftsize)) 
        
        # 将振幅大于-80dB的频率输出
        peak_index = (fft_data > -80)
        peak_value = fft_data[peak_index][:20]
        result = []
        for f, v in zip(np.flatnonzero(peak_index), peak_value):
            result.append("%02d : %g" %(f, v) )
        self.peak_list = "\n".join(result)
   
        self.ax1.relim()
        self.ax1.autoscale_view()     
        self.plot_sin_combine()
        
    @on_trait_change("N") 
    def plot_sin_combine(self):
        index, data = fft_combine(self.fft_parameters, self.N, 2)
        self.line_wave2.set_ydata(data)
        self.ax2.relim()
        self.ax2.autoscale_view()
        if self.figure.canvas is not None:
            self.figure.canvas.draw()


if __name__ == "__main__":
    fft_demo = FFTDemo()
    fft_demo.configure_traits()