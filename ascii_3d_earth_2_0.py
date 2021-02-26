import pygame as pg
import numpy as np
from math import pi, sin, cos

clock = pg.time.Clock()
FPS = 30

WIDTH = 1920
HEIGHT = 1080

R = 300
R_moon = R / 3.7
MAP_WIDTH = 139
MAP_HEIGHT = 34

MAP_WIDTH_MOON = 49
MAP_HEIGHT_MOON = 15

black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
grey = (100, 100, 100)
dark_grey = (50, 50, 50)

pg.init()

my_font = pg.font.SysFont('arial', 20)
my_font_moon = pg.font.SysFont('arial', 12)

with open('earth_2_0_W140_H35.txt', 'r') as file:
    data = [file.read().replace('\n', '')]

ascii_chars = []
for line in data:
    for char in line:
        ascii_chars.append(char)

inverted_ascii_chars = ascii_chars[::-1]

with open('moon_W50_H16.txt', 'r') as file:
    data = [file.read().replace('\n', '')]

moon_ascii_chars = []
for line in data:
    for char in line:
        moon_ascii_chars.append(char)

inverted_moon_ascii_chars = moon_ascii_chars[::-1]


class Projection:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        self.background = (black)
        pg.display.set_caption('ASCII 3D EARTH')
        self.surfaces = {}

    def addSurface(self, name, surface):
        self.surfaces[name] = surface

    def display(self):
        self.screen.fill(self.background)

        for key, value in self.surfaces.items():
            if key == 'globe':
                i = 0
                for node in value.nodes:
                    self.text = inverted_ascii_chars[i]
                    self.text_surface = my_font.render(self.text, False, (green if self.text == '+' else blue))
                    self.text_surface_dark = my_font.render(self.text, False, (grey if self.text == '+' else dark_grey))
                    if node[0] > 0 and node[1] > 0:
                        self.screen.blit(self.text_surface, (WIDTH / 2 + int(node[0]), HEIGHT / 2 + int(node[2])))
                    if node[0] < 0 and node[1] > 0:
                        self.screen.blit(self.text_surface_dark, (WIDTH / 2 + int(node[0]), HEIGHT / 2 + int(node[2])))
                    i += 1
            elif key == 'moon':
                j = 0

                center = value.findCentre()

                for node in value.nodes:
                    self.text = inverted_moon_ascii_chars[j]
                    self.text_surface = my_font_moon.render(self.text, False, grey)
                    self.text_surface_dark = my_font_moon.render(self.text, False, dark_grey)
                    if node[0] > center[0] and node[0] > R and node[1] > -R / 3 * 2 or node[0] > center[0] and node[
                        0] < -R and node[1] > -R / 3 * 2 or node[0] > center[0] and node[0] > -R and node[0] < R and \
                            node[1] > 0:
                        self.screen.blit(self.text_surface, (WIDTH / 2 + int(node[0]), HEIGHT / 2 + int(node[2])))
                    if node[0] < center[0] and node[0] > R and node[1] > -R / 3 * 2 or node[0] < center[0] and node[
                        0] < -R and node[1] > -R / 3 * 2 or node[0] < center[0] and node[0] > -R and node[0] < R and \
                            node[1] > 0:
                        self.screen.blit(self.text_surface_dark, (WIDTH / 2 + int(node[0]), HEIGHT / 2 + int(node[2])))
                    j += 0

    def moveAll(self, theta):

        for key, value in self.surfaces.items():
            if key == 'globe':

                center = value.findCentre()

                c = np.cos(theta)
                s = np.sin(theta)

                # Rotating about Z - axis
                rotate_matrix = np.array([[c, -s, 0, 0],
                                          [s, c, 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])

                value.rotate(center, rotate_matrix)

            elif key == 'moon':

                center = value.findCentre()

                c = np.cos(theta)
                s = np.sin(theta)

                # Rotating about Z - axis
                rotate_matrix = np.array([[c, -s, 0, 0],
                                          [s, c, 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])

                dx = R * 2 * np.cos(theta)
                dy = R * 2 * np.sin(theta)
                dz = 0

                # Moving coordinates
                transform_matrix = np.array([[1, 0, 0, 0],
                                             [0, 1, 0, 0],
                                             [0, 0, 1, 0],
                                             [dx, dy, dz, 1]])

                scale_a = 0.5
                scale_b = 1

                scale_c = scale_b - scale_a
                scale_d = scale_c / 2

                if dy != 0:
                    sx = sy = sz = (scale_c + scale_d) + (scale_d / (R * 2)) * dy
                else:
                    sx = sy = sz = (scale_c + scale_d)

                # Scaling coordinates
                scale_matrix = np.array([[sx, 0, 0, 0],
                                         [0, sy, 0, 0],
                                         [0, 0, sz, 0],
                                         [0, 0, 0, 1]])

                value.rotate(center, rotate_matrix)
                value.transform(transform_matrix)
                value.scale(center, scale_matrix)


class Object:
    def __init__(self):
        self.nodes = np.zeros((0, 4))

    def addNodes(self, node_array):
        ones_column = np.ones((len(node_array), 1))
        ones_added = np.hstack((node_array, ones_column))
        self.nodes = np.vstack((self.nodes, ones_added))

    def findCentre(self):
        mean = self.nodes.mean(axis=0)
        return mean

    def rotate(self, center, matrix):
        for i, node in enumerate(self.nodes):
            self.nodes[i] = center + np.matmul(matrix, node - center)

    def transform(self, matrix):
        self.nodes = np.dot(self.nodes, matrix)

    def scale(self, center, matrix):
        for i, node in enumerate(self.nodes):
            self.nodes[i] = center + np.matmul(matrix, node - center)


xyz = []

for i in range(MAP_HEIGHT + 1):
    lat = (pi / MAP_HEIGHT) * i
    for j in range(MAP_WIDTH + 1):
        lon = (2 * pi / MAP_WIDTH) * j
        x = round(R * sin(lat) * cos(lon), 2)
        y = round(R * sin(lat) * sin(lon), 2)
        z = round(R * cos(lat), 2)
        xyz.append((x, y, z))

xyz_moon = []

for i in range(MAP_HEIGHT_MOON + 1):
    lat = (pi / MAP_HEIGHT_MOON) * i
    for j in range(MAP_WIDTH_MOON + 1):
        lon = (2 * pi / MAP_WIDTH_MOON) * j
        x = round(R_moon * sin(lat) * cos(lon), 2)
        y = round(R_moon * sin(lat) * sin(lon), 2)
        z = round(R_moon * cos(lat), 2)
        xyz_moon.append((x, y, z))

spin = 0

running = True
while running:

    clock.tick(60)

    pv = Projection(WIDTH, HEIGHT)

    earth = Object()
    moon = Object()
    earth_nodes = [i for i in xyz]
    moon_nodes = [i for i in xyz_moon]
    earth.addNodes(np.array(earth_nodes))
    moon.addNodes(np.array(moon_nodes))
    pv.addSurface('globe', earth)
    pv.addSurface('moon', moon)
    pv.moveAll(spin)
    pv.display()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    pg.display.update()
    spin -= 0.03
