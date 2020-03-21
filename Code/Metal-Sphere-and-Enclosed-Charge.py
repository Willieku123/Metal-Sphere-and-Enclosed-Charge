from visual import*
from visual.graph import*
import wx
import random
import time


# Variables
ball_size = 0.8
k = 150
drag_k = 40
t = 0
dt = 0.0005

#VPython initialization 
window = window(menus=True, title="I bet nobody could notice this weird title",x=0, y=0, width=1490, height=840)
scene = display(window=window, x=10, y=10, height=820, width=820, autoscale=False,
                title = "Try pressing O&P !!")
gd = gdisplay(window=window, x=840, y=10, width=500, height=500, ymax=4000, xtitle="t", ytitle="total V")
f1 = gcurve(color=color.green)

#get vertex positions from vertex_list_sub2.txt
file = open("vertex_list_sub2.txt")
text = file.read()
file.close()
midway1 = text[1:-2].split("],[")
midway2 = [i.split(",") for i in midway1]
vertex = [[float(x), float(y), float(z)] for x, y, z in midway2]

# Class particle
class Particle():

    def __init__(self, q, pos, vel, acc, m, r, ball_color=color.white):
        self.q = q
        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.m = m
        if q > 0:
            ball_color = color.red
        else:
            ball_color = color.blue
        self.ball = box(pos=norm(pos)*r, height=ball_size, width=ball_size, length=ball_size,
                        color=(ball_color), make_trail=False, retain=200)
        self.pointer = arrow(pos = self.pos, color = color.white, shaftwidth = ball_size*0.3, visible=0)
        self.r = r
        self.force = vector(0,0,0)

    def update(self):
        self.pos += self.vel * dt
        self.vel += self.acc * dt
        self.vel = self.vel - dot(self.vel, self.pos) / abs(self.pos) * norm(self.pos)
        self.pos = norm(self.pos)*self.r
        self.ball.pos = self.pos
        self.pointer.pos = self.pos
        self.pointer.axis = self.force * 0.001

# Declare inner wall
particles = [Particle(q=10, pos=vector(i), vel=vector(0, 0, 0), acc=vector(0, 0, 0), m=1, r=10) for i in vertex]

# Declare outer wall
for i in vertex:
    particles.append(Particle(q=-10, pos=vector(i), vel=vector(0, 0, 0), acc=vector(0, 0, 0), m=1, r=20))
for i in particles:
    i.pos *= i.r

# Declare point charge
point_e = Particle(q=-10*len(vertex), pos=vector([0, 0, 0]), vel=vector([0, 0, 0]), acc=vector([0, 0, 0]), m=10, r=0)
point_e.ball.color = color.white

point_e.ball.width = 1.6
point_e.ball.height = 1.6
point_e.ball.length = 1.6

inner_ball = sphere(pos=(0, 0, 0), radius=10, opacity=0.8, color=color.gray(0.4))
outer_ball = sphere(pos=(0, 0, 0), radius=20, opacity=0.1, color=color.gray(0.4))

# Light setting
scene.ambient=color.gray(0.5)

# Ugly UI 
def change_inner_opacity(evt):
    inner_ball.opacity = 0.9 - inner_ball.opacity
def change_outer_opacity(evt):
    outer_ball.opacity = 0.9 - outer_ball.opacity
def change_pointer_opacity(evt):
    for i in particles:
        i.pointer.visible = i.pointer.visible*-1 - 1
def change_point_e_pos(evt):
    point_e.pos.x = point_e_slider.GetValue()
    point_e.ball.pos.x = point_e_slider.GetValue()

p = window.panel
wx.StaticText(p, pos=(1045,520), label='Display/Hide:')

change_inner_button = wx.Button(p,label = 'Inner Wall', size = (130,30), pos = (880,540))
change_inner_button.Bind(wx.EVT_BUTTON, change_inner_opacity)

change_outer_button = wx.Button(p,label = 'Outer Wall', size = (130,30), pos = (1020,540))
change_outer_button.Bind(wx.EVT_BUTTON, change_outer_opacity)

change_pointer_button = wx.Button(p,label = 'Force Arrows', size = (130,30), pos = (1160,540))
change_pointer_button.Bind(wx.EVT_BUTTON, change_pointer_opacity)

wx.StaticText(p, pos=(1010,590), label='Set point charge\'s position')
wx.StaticText(p, pos=(888,640), label='0')
wx.StaticText(p, pos=(1015,640), label='r')
wx.StaticText(p, pos=(1138,640), label='2r')
wx.StaticText(p, pos=(1265,640), label='3r')

point_e_slider = wx.Slider(p, pos=(880,620), size=(400,20), minValue=0, maxValue=30)
point_e_slider.Bind(wx.EVT_SCROLL, change_point_e_pos)

wx.StaticText(p, pos=(880,680), label='* Hold right key to rotate, and hold middle key to zoom in/out')

# Loop, obviously
while True:
    rate(1/dt)
    t += dt

    # Calculate force, velocity and position of every charges
    s = vector(0, 0, 0)
    for i in particles:
        total_force = vector(0, 0, 0)
        total_force_without_restraint = vector(0,0,0)
        for j in particles:
            if i is j:
                continue
            else:
                distance = (i.pos - j.pos)
                force = (k*i.q*j.q)*distance/abs(distance)**3
                total_force_without_restraint += force
                force2 = force - dot(force, i.pos)/abs(i.pos) * norm(i.pos)
                total_force += force2


        distance = (i.pos - point_e.pos)
        force = (k*i.q*point_e.q)*distance/abs(distance)**3
        
        i.force = total_force_without_restraint - i.vel * drag_k + force

        force2 = force - dot(force, i.pos)/abs(i.pos) * norm(i.pos)
        total_force += force2 - i.vel * drag_k

        i.acc = total_force/i.m
        s += i.vel

    for i in particles:
        i.update()

    # Draw the chart
    f1.plot(pos=(t, abs(s)))
