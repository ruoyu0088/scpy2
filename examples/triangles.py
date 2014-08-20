import numpy as np
import pylab as pl
from OpenGL.GL import *
from OpenGL.GLUT import *

class OpenGLErrorEvaluater(object):
    def __init__(self, img, n):
        self.width, self.height = img.shape[:2]
        self.n = n
        self.img = img.astype(float)
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow("glut sample")

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        self.points = np.zeros((self.n, 6), np.float32)
        self.colors = np.zeros((self.n, 3, 4), np.float32)
        self.index = np.arange(3*self.n)
        self.buf = np.empty((self.height, self.width, 4), dtype=np.uint8)

        glVertexPointerf(self.points.reshape(3*self.n, 2))
        glColorPointerf(self.colors.reshape(3*self.n, 4))

    def draw(self, individual):
        individual = individual.reshape(-1, 10)
        self.points[:] = individual[:, :6]
        self.points[:] *= 2
        self.points[:] -= 1
        self.colors[:] = individual[:, None, 6:]
        glClearColor(1, 1, 1, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glDrawElements(GL_TRIANGLES, 3*self.n, GL_UNSIGNED_INT, self.index)
        glFlush()
        glutMainLoopEvent()
        glReadPixels(0, 0, self.width , self.height, GL_BGRA, GL_UNSIGNED_BYTE, array=self.buf)
        return self.buf[:, :, :3]

    def error(self, individual):
        buf = self.draw(individual)
        err = float(np.sum(np.abs(buf.astype(float)-img)))
        err = err / (self.width * self.height * 3.0)
        return float(err),


class HallOfFame(object):
    def __init__(self):
        self.last_error = 10000
        self.count = 0

    def update(self, pop):
        error = min(p.fitness.values[0] for p in pop)
        if self.last_error - 0.5 > error:
            p = min(pop, key=lambda p:p.fitness.values[0])
            buf = ee.draw(p)
            cv2.imwrite("gen_{:07d}.png".format(self.count), buf)
            self.last_error = error
        self.count += 1


import cv2
img = cv2.imread("firefox.png")
img = cv2.resize(img, (128, 128))
N = 300
ee = OpenGLErrorEvaluater(img, N)

import random

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", np.ndarray, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
# Attribute generator
toolbox.register("attr_bool", random.random)
# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, N*10)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Operator registering
toolbox.register("evaluate", ee.error)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.5, indpb=0.5)
toolbox.register("select", tools.selTournament, tournsize=3)

pop = toolbox.population(n=40)
hof = HallOfFame()
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

def cxTwoPoint(ind1, ind2):
    _ind1 = ind1.reshape(-1, 10)
    _ind2 = ind2.reshape(-1, 10)
    size = ee.n
    p1 = random.randint(1, size)
    p2 = random.randint(1, size-1)
    if p2 >= p1:
        p2 += 1
    else:
        p1, p2 = p2, p1
    s = slice(p1, p2, 1)
    tmp = _ind1[s].copy()
    _ind1[s] = _ind2[s]
    _ind2[s] = tmp
    return ind1, ind2

toolbox.register("mate", cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.1, indpb=0.0005)
toolbox.register("select", tools.selTournament, tournsize=3)
pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.5, ngen=400000,
                               stats=stats, halloffame=hof, verbose=True)