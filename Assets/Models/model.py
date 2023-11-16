import math
import sys

def cross(a, b, c):
    d = [(a[1] - b[1]) * (c[2] - b[2]) - (a[2] - b[2]) * (c[1] - b[1]),
         (a[2] - b[2]) * (c[0] - b[0]) - (a[0] - b[0]) * (c[2] - b[2]),
         (a[0] - b[0]) * (c[1] - b[1]) - (a[1] - b[1]) * (c[0] - b[0])]

    return d

f = open("wheel.obj", "w")
f.write("#Wheel.obj\n\n")
f.write("g Wheel\n\n")

# Number of points that define cylinder
points = 8
if (sys.argv[1] and int(sys.argv[1]) >= 3 and int(sys.argv[1]) <= 360):
    points = int(sys.argv[1])
radius = 1
if (sys.argv[2]):
    radius = float(sys.argv[2])
width = 0.5
if (sys.argv[3]):
    width = float(sys.argv[3])
angle = 2 * math.pi / points
coordinates = [[0, 0, 0], [0, 0, width]]

# Create center points of circle faces
f.write("v 0 0 0\n")
f.write("v 0 0 {}\n".format(width))

# Create coordinates of the outer mesh
for i in range(points):
    coordinates.append([radius * math.sin(angle * i), radius * math.cos(angle * i), 0])
    coordinates.append([radius * math.sin(angle * i), radius * math.cos(angle * i), width])
    f.write("v {:.2f} {:.2f} {:.2f}\n".format(coordinates[-2][0], coordinates[-2][1], 0))
    f.write("v {:.2f} {:.2f} {:.2f}\n".format(coordinates[-1][0], coordinates[-2][1], width))

# Create vector normals for circle faces
f.write("\nvn 0 0 1\n")
f.write("vn 0 0 -1\n")

# Create vector normals for outer edge
for i in range(3, points * 2, 2):
    normal = cross(coordinates[i], coordinates[i + 1], coordinates[i + 2])
    f.write("vn {} {} {}\n".format(normal[0], normal[1], normal[2]))
normal = cross(coordinates[points * 2 + 1], coordinates[2], coordinates[3])
f.write("vn {} {} {}\n".format(normal[0], normal[1], normal[2]))

f.write("\n")
# Create faces of circle
for i in range(3, points * 2, 2):
    f.write("f {}//2 {}//2 1//2\n".format(i, i + 2))
    f.write("f 2//1 {}//1 {}//1\n".format(i + 3, i + 1))
f.write("f {}//2 3//2 1//2\n".format(points * 2 + 1))
f.write("f 2//1 4//1 {}//1\n".format(points * 2 + 2))

normal = 3
# Create faces of outer edge
for i in range(3, points * 2 + 1, 2):
    f.write("f {}//{} {}//{} {}//{}\n".format(i, normal, i + 1,normal, i + 2, normal))
    f.write("f {}//{} {}//{} {}//{}\n".format(i + 3,normal, i + 2,normal, i + 1, normal))
    normal = normal + 1
f.write("f {}//{} {}//{} 3//{}\n".format(points * 2 + 1,normal,  points * 2 + 2, normal, normal))
f.write("f 4//{} 3//{} {}//{}\n".format(normal, normal, points * 2 + 2, normal))

f = open("wheel.obj", "r")
print(f.read())

f.close()