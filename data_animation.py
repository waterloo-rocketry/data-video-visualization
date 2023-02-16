from matplotlib import pyplot as plt
import matplotlib.animation as animation
import pandas as pd

from matplotlib.animation import FuncAnimation, writers

plt.rcParams['animation.ffmpeg_path'] = r"C:\FFMPEG\bin\ffmpeg.exe"

# Needs to be configured depending on what headings are given to the data
m = pd.read_csv("examples/SF6 animation data.csv")

ctime = m['Timestamp'][:-250]
cmass = m['Omega S-Type - Ox Tank Mass']
coxpressure = m['PT-2 Ox Tank']
c_cc_pressure = m['PT-3 CC']
cthrust = m['Thrust']

c_dp = m['dP']

fig = plt.figure()
ax1 = fig.add_subplot(111)

ttime = []

tmass = []
tmass_line, = ax1.plot([], [], label = "Omega S-Type - Ox Tank Mass", color = 'black')

toxpressure = []
toxpressureline, = ax1.plot([], [], label = "PT-2 Ox Tank", color = 'blue')

t_ccpressure = []
t_ccpressure_line, = ax1.plot([], [], label = "PT-3 CC", color = 'green')

tthrust = []
tthrust_line, = ax1.plot([], [], label = "Thrust", color = 'red')

ax1.set_xlim([ctime.iloc[0], 25])
ax1.set_ylim(0,1000)
ax1.legend(loc = 'upper right')

def animate(i):
    ttime.append(ctime[i])

    tmass.append(cmass[i])
    t_ccpressure.append(c_cc_pressure[i])
    tthrust.append(cthrust[i])
    toxpressure.append(coxpressure[i])
    
    tmass_line.set_data(ttime, tmass)
    t_ccpressure_line.set_data(ttime, t_ccpressure)
    tthrust_line.set_data(ttime, tthrust)
    toxpressureline.set_data(ttime, toxpressure)


# The interval and frames have to add up to the fps set later for the video to be real-time accurate
ani = animation.FuncAnimation(fig, animate, interval = 25, frames = 1250, repeat = False) 

f = r"examples/animation.mp4"
Writer = animation.writers['ffmpeg']
writer = Writer(fps=50, metadata=dict(artist='Waterloo Rocketry Team'))
ani.save(f, writer=writer)

plt.show()
print('Video saved sucessfully')
