# import tools
import pygame
from math import *
import sys
import pygame.gfxdraw
import numpy as np
import os


class objectGeneration:

    def __init__(self):
        '''
            Initializing all required constants and variables

            :param WINDOW_SIZE: size of PyGame window
            :param WINDOW: PyGame window to display 3D object
            :param PROJECTION_MATRIX: used to convert a vertex in 3D space to 2D
            :param SCALE: to scale or increase the distance between vertices to view 3D object
            :param COLOR_PER_ANGLE: how much color to change per degree rotation. Converted HEX value of colors to RGB [#00005F to (0, 0, 95) and #0000FF to (0, 0, 255)]
            :param VERTICES: number of vertices for given 3D figure in object.txt file
            :param FACES: umber of faces for given 3D figure in object.txt file
            :param LINES: lines to read from object.txt file
            :param angle_x: angle rotated w.r.t x-axis
            :param angle_y: angle rotated w.r.t y-axis
            :param angle_z: angle rotated w.r.t z-axis
            :param surfaces: list of faces with their respective vertices.
        '''

        self.WINDOW_SIZE =  600
        self.WINDOW = pygame.display.set_mode( (self.WINDOW_SIZE, self.WINDOW_SIZE) )
        self.PROJECTION_MATRIX = [[1,0,0],
                            [0,1,0],
                            [0,0,0]]

        self.SCALE = 100
        self.COLOR_PER_ANGLE = abs((255-95)/90)
        self.VERTICES = 0
        self.FACES = 0
        self.LINES = []

        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.surfaces = []


    def readInput(self):
        '''
            Method to read object.txt file, construct figure_matrix a matrix of vertices and to create a list of surfaces with their respective vertices.

            :param figure_matrix: a matrix of vertices, consists of 3D vertices which is used to convert them to 2D vertices
            :param figure_points: list of coordinates of each vertices given
        '''

        with open(os.path.join(sys.path[0], "object.txt"), "r") as f:
            self.LINES = f.readlines()
            self.VERTICES, self.FACES = self.LINES[0].strip().split(",")
            self.VERTICES, self.FACES = int(self.VERTICES), int(self.FACES)
            figure_matrix = [n for n in range(int(self.VERTICES))]
            figure_points = [n for n in range(int(self.VERTICES))]

            for i in range(1, self.VERTICES+1):
                coord = self.LINES[i].strip().split(",")
                figure_matrix[i-1] = [[int(float(coord[1]))], [int(float(coord[2]))], [int(float(coord[3]))]]
                figure_points[i-1] = [int(float(coord[1])), int(float(coord[2])), int(float(coord[3]))]

            for j in range(self.VERTICES + 1, self.VERTICES + self.FACES + 1):
                surface = []
                for k in range(len(self.LINES[self.VERTICES + 1].strip().split(","))):
                    surface.append(int(float(self.LINES[j].strip().split(",")[k])) - 1)

                self.surfaces.append(surface)

        return figure_matrix, figure_points

    def multiply_m(self, a, b):
        '''
            Method to multiple two matrices of compatible dimensions

            :param product: resultant matrix after multiplication
        '''

        a_rows = len(a)
        a_cols = len(a[0])

        b_rows = len(b)
        b_cols = len(b[0])

        product = [[0 for _ in range(b_cols)] for _ in range(a_rows)]

        if a_cols == b_rows:
            # Dot product matrix dimentions = a_rows x b_cols
            product = np.dot(a,b)
        else:
            print("INCOMPATIBLE MATRIX SIZES")

        return product


    def connect_points(self, i, j, points):
        '''
            Method to draw line segments to connect vertices
        '''

        pygame.draw.line(self.WINDOW, (0, 0, 0), (points[i-1][0], points[i-1][1]) , (points[j-1][0], points[j-1][1]), width=3)


    def rotate3dto2d(self, figure_matrix):
        '''
            Method to convert 3D vertices to 2D vertices to be displayed on 2D plain

            :param rotation_x: matrix to rotate vertices along x-axis
            :param rotation_y: matrix to rotate vertices along y-axis
            :param rotation_z: matrix to rotate vertices along z-axis
            :param points: list of coordinates of vertices in 2D space
        '''

        rotation_x = [[1, 0, 0],
                        [0, cos(self.angle_x), -sin(self.angle_x)],
                        [0, sin(self.angle_x), cos(self.angle_x)]]

        rotation_y = [[cos(self.angle_y), 0, sin(self.angle_y)],
                        [0, 1, 0],
                        [-sin(self.angle_y), 0, cos(self.angle_y)]]

        rotation_z = [[cos(self.angle_z), -sin(self.angle_z), 0],
                        [sin(self.angle_z), cos(self.angle_z), 0],
                        [0, 0, 1]]

        points = [0 for _ in range(len(figure_matrix))]

        i = 0
        for point in figure_matrix:
            rotate_x = self.multiply_m(rotation_x, point)
            rotate_y = self.multiply_m(rotation_y, rotate_x)
            rotate_z = self.multiply_m(rotation_z, rotate_y)
            point_2d = self.multiply_m(self.PROJECTION_MATRIX, rotate_z)

            x = (point_2d[0][0] * self.SCALE) + self.WINDOW_SIZE/2
            y = (point_2d[1][0] * self.SCALE) + self.WINDOW_SIZE/2

            points[i] = (x,y)
            i += 1
            pygame.draw.circle(self.WINDOW, (255, 0, 0), (x, y), 5)

        return points

    def drawLines(self, points):
        '''
            Method to find the vertices between which we need to draw a line segment
        '''

        for j in range(int(self.VERTICES) + 1, int(self.VERTICES)+ int(self.FACES) + 1):
            for k in range(len(self.LINES[int(self.VERTICES) + 1].strip().split(",")) - 1):
                self.connect_points(int(float(self.LINES[j].strip().split(",")[k])), int(float(self.LINES[j].strip().split(",")[k+1])), points)

            self.connect_points(int(float(self.LINES[j].strip().split(",")[0])), int(float(self.LINES[j].strip().split(",")[len(self.LINES[int(self.VERTICES) + 1].strip().split(",")) - 1])), points)


    def mainfun(self, figure_matrix, figure_points):
        '''
            To convert a 3D figure to be displayed on 2D plain we first need to convert every 3D vertex to 2D. For this we use matrix multiplication of projection matrix for 3D
            space with every 3D point to get 2D point. For rotation, we rotate tthe figure in 3D and then project on 2D plain. we use the 3x3 rotation matrix for x,y,z axis to
            transform a 3D vertex to another 3D point after rotation.

            Next to make the rotation based on mouse movement, we calculate the initial mouse position on screen and update the x, y coordinates as mouse position changes.
            dx: mouse position change in x direction
            dx: mouse position change in y direction

            update angle of rotation in x and y direction based on 'self.angle_x + (dy/self.WINDOW_SIZE)*360*(0.0174533)' formula

            the formula finds the percentage of change w.r.t window size and finds the corresponding percent change in angle in radians - both for x and y
        '''

        lastPosX = lastPosY = 0

        while True:
            self.WINDOW.fill((255, 255, 255))

            points = self.rotate3dto2d(figure_matrix)

            self.drawLines(points)

            self.rotate3dto2d(figure_matrix)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                    x, y = pygame.mouse.get_pos()
                    dx = x - lastPosX
                    dy = y - lastPosY

                    self.angle_x = self.angle_x + (dy/self.WINDOW_SIZE)*360*(0.0174533)

                    self.angle_y = self.angle_y + (dx/self.WINDOW_SIZE)*360*(0.0174533)

                    lastPosX = x
                    lastPosY = y

            pygame.display.update()

if __name__ == "__main__":
    objg = objectGeneration()
    figure_matrix, figure_points = objg.readInput()
    objg.mainfun(figure_matrix, figure_points)
