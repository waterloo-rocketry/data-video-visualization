from matplotlib import pyplot as plt
import matplotlib.animation as animation
import pandas as pd

from matplotlib.animation import FuncAnimation, writers
# from mat
from scipy.signal import savgol_filter

plt.rcParams['animation.ffmpeg_path'] = r"C:\FFMPEG\bin\ffmpeg.exe"

# Needs to be configured depending on what headings are given to the data
m = pd.read_csv("working_directory/2023_01_29-03_09_58_PM.csv")

# print(m.keys())
# ctime = m['Timestamp'][:-250]
cmass = m['Honeywell S-type (Ox tank)']
cmass = savgol_filter(cmass, 2500, 2)
# cmass = 
cinjector = m['PT-3 Injector']
cinjector = savgol_filter(cinjector, 2500, 2)
# c_cc_pressure = m['PT-3 CC']
cthrust = m['Thrust']

# c_dp = m['dP']

fig = plt.figure()
ax1 = fig.add_subplot(111)

ttime = []



tinjector = []
toxpressureline, = ax1.plot([], [], label = "PT-3 Injector (psi)", color = 'blue')

# t_ccpressure = []
# t_ccpressure_line, = ax1.plot([], [], label = "PT-3 CC", color = 'green')

tthrust = []
tthrust_line, = ax1.plot([], [], label = "Thrust (lbf)", color = 'red')

ax1.set_xlim(0, 20)
ax1.set_ylim(-100, 3000)
ax1.set_ylabel('psi/lbf')


ax2 = ax1.twinx()  
ax2.set_ylim(0, 100)
ax2.set_ylabel('kg')

tmass = []
tmass_line, = ax2.plot([], [], label = "Omega S-Type - Ox Tank Mass (kg)", color = 'black')

ax1.legend(loc = 'upper left')
ax2.legend(loc = 'upper right')

global time
time = 0
tsamp = 0.02

def animate(i):
    global time
    ttime.append(time)
    time += tsamp

    tmass.append(cmass[i*100])
    # t_ccpressure.append(c_cc_pressure[i])
    tthrust.append(cthrust[i*100])
    tinjector.append(cinjector[i*100])
    
    tmass_line.set_data(ttime, tmass)
    # t_ccpressure_line.set_data(ttime, t_ccpressure)
    tthrust_line.set_data(ttime, tthrust)
    toxpressureline.set_data(ttime, tinjector)


# The interval and frames have to add up to the fps set later for the video to be real-time accurate
ani = animation.FuncAnimation(fig, animate, interval = 20, frames = 1000, repeat = False) 

f = r"working_directory/sf7_animation.mp4"
Writer = animation.writers['ffmpeg']
writer = Writer(fps=50, metadata=dict(artist='Waterloo Rocketry Team'))
ani.save(f, writer=writer) # Comment out this line to get a 'preview' via the matplotlib plot

plt.show()
print('Video saved sucessfully')
