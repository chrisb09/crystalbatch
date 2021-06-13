#!/bin/python3
import math, json, cairo, os

#border_color = (1,1,1) #White
border_color = (0,0,0) #Black

border_width = 2

folder = "output"

if not os.path.exists(folder):
    os.mkdir(folder)
 
f = open('structure.json',)
data = json.load(f)
f.close()

bounds = [math.inf,math.inf,-math.inf,-math.inf]

pady = 36
padx = 117

for p in data["Points"]:
    x = p[0]
    y = p[1]
    if x < bounds[0]:
        bounds[0] = x
    if y < bounds[1]:
        bounds[1] = y
    if x > bounds[2]:
        bounds[2] = x
    if y > bounds[3]:
        bounds[3] = y

print(bounds)
w = bounds[2]-bounds[0]
h = bounds[3]-bounds[1]

print(str(w)+"x"+str(h))
print(str(w+padx)+"x"+str(h+pady))

points = []

for p in data["Points"]:
    x = p[0] - bounds[0] + padx/2
    y = p[1] - bounds[1] + pady/2
    points.append([x,576-y])
    

def _color_to_int(color):
    value = (color)[0]
    for i in range(1, len(color)):
        value = (value << 8) + (color)[i]
    return value

def _int_to_color(color):
    v = []
    for i in range(4):
        v.append((color & (255 << 8*(3-i))) >> 8*(3-i))
    return v

def _rel_color(color):
    r = []
    for c in color:
        r.append(c / 255.0)
    return tuple(r)


def _draw_form(context, points, point_indices, color):
    context.move_to(*points[point_indices[0]])
    for i in range(len(point_indices)):
        p = points[point_indices[(i+1)%len(point_indices)]]
        context.line_to(p[0], p[1])
    context.set_source_rgba(*color)
    context.fill()
    context.stroke()
    
    for i in range(len(point_indices)):
        q = points[point_indices[(i)%len(point_indices)]]
        context.move_to(*q)
        p = points[point_indices[(i+1)%len(point_indices)]]
        context.line_to(*p)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_width(border_width)
        context.set_source_rgba(*border_color, 1)
        context.stroke()

def _draw(keys):

    WIDTH, HEIGHT = 576, 576

    surface = cairo.SVGSurface(folder+"/"+str(len(keys))+".svg", 576, 576)

    context = cairo.Context(surface)

    for crystal in keys:
        #colors = (random.random(),random.random(),random.random())
        colorint = int(data["Stones"][crystal]["Color"],16)
        colors = _rel_color(_int_to_color(colorint))
        print(colors)
        for l in data["Stones"][crystal]["Polygons"]:
            _draw_form(context, points, l, colors)
            
keys = []
_draw(keys)
for k in data["Order"]:
    keys.append(k)
    _draw(keys)
    
print("Done.")
