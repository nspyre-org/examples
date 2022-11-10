#!/usr/bin/env python3

"""Routines to perform real-time plotting of  data from a temperature controller"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FormatStrFormatter
import time
import datetime as dt

_line_styles = ['r-',
                'b-', 
                'g-', 
                'c-', 
                'm-', 
                'y-', 
                'k-']

class TcPlot():
    def __init__(self, heater_names, thermometer_names, duration=120):
        """
        
        Keyword Parameters: 
           heater_names
           thermometer_names
           duration            (in seconds)
        """
        assert (len(heater_names)+len(thermometer_names)) <= len(_line_styles), f"We don't have enough colors for {len(samples)} samples.  Maximum is {len(_line_styles)}."

        self.heater_names      = heater_names
        self.thermometer_names = thermometer_names
        self.x                 = []
        self.ys                = [[]] * (len(heater_names) + len(thermometer_names))

        self.Span = duration      # timespan to plot (in seconds)
        self.PaintInterval = 1.0  # period between plot updates (in seconds)
        self.Closed = False       # has user closed the plot window?
        self.OnClosed = None      # callback function called on window close.

        # Create the plot
        self.fig, self.ax1 = plt.subplots()

        # Hook the close click event
        self.fig.canvas.mpl_connect('close_event', self.handle_close)

        # Enable interactive mode
        plt.ion()

        # Init primary axis
        self.ax1.set_xlabel('time (s)')                
        self.ax1.set_ylabel('Heater (W)', color='r')
        self.ax1.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
        self.ax1.tick_params('y', colors='r')
        self.ax1.grid(color='r', linestyle=':', linewidth=1)
        
        # Init secondary axis
        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel('Temp (K)', color='b')
        self.ax2.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
        self.ax2.tick_params('y', colors='b')
        self.ax2.grid(color='b', linestyle=':', linewidth=1)
        
        # Create a line for each heater and sensor
        self.lines = [None] * len(self.ys)
        for i in range(len(self.lines)):
            self.lines[i], = self._axis(i).plot(self.x, self.ys[i], _line_styles[i])

        # Add a legend to the plot.
        labels = [f"{h} (W)" for h in self.heater_names]+[f"{t} (K)" for t in self.thermometer_names]
        plt.legend(self.lines, labels, loc='upper left')

        self.clear()
        plt.show()
        
        self.lastPaintTime = dt.datetime.now()

    def _axis(self, i):
        """Lookup which axis to plot the i'th line onto.

        Heaters plot on the first axis, thermometers plot on the second.

        Keyword Parameters:
          i   index into the lines array.
        """
        ax = self.ax1
        if i >= len(self.heater_names): ax = self.ax2
        return ax

        
    def setWindowTitle(self, title):
        self.fig.canvas.set_window_title(title)

    def handle_close(self, evt):
        # Indicate the plot has been closed
        self.Closed = True

        # Call event handler, if set
        if self.OnClosed is not None:
            self.OnClosed()

    def clear(self):
        
        # Remove all existing data
        self.x  = []
        self.ys = [[]] * len(self.ys)
        
        # Capture the start time to calculate elapsed time later within update()
        self.start = dt.datetime.now()

    def update(self, heaters, thermometers):
        """y1 = Heater power, y2 = Temperature"""

        samples = heaters + thermometers

        assert len(samples) == len(self.ys), f"Must provide a total of {len(samples)} samples."
        
        if self.Closed:
            return

        # Capture the total elapsed time since the plot has been started
        n      = dt.datetime.now()
        deltaT = (n - self.start)
        elapsed = deltaT.total_seconds()

        # Capture the minimum timestamp of data allowed to remain within the plot
        minsec = elapsed - self.Span

        # Delete all data that is too old
        while len(self.x) > 0 and self.x[0] < minsec:
            self.x = self.x[1:]
            for i in range(len(self.ys)):
                self.ys[i] = self.ys[i][1:]

        # Add the new samples
        self.x.append(elapsed)
        for i in range(len(self.ys)):
            self.ys[i] = self.ys[i] + [samples[i]]

        # Calc the time elasped since the last paint of the plot
        elapsed = (dt.datetime.now() - self.lastPaintTime).total_seconds()

        if elapsed >= self.PaintInterval:
            # Repaint the plot

            self.lastPaintTime = dt.datetime.now()

            for i in range(len(self.lines)):
                self.lines[i].set_xdata(self.x)
                self.lines[i].set_ydata(self.ys[i])

            self.ax1.relim()
            self.ax1.autoscale_view()

            self.ax2.relim()
            self.ax2.autoscale_view()

        # Redraw        
        self.fig.canvas.draw()
        plt.pause(0.001)

