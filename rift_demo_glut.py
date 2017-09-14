#!/bin/env python

import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import sys

sys.path.append("procon28_pyovr/ovr")
from rift_gl_renderer_compatibility import RiftGLRendererCompatibility


WIDTH = 1280 
HEIGHT = 720
N_RANGE = 1.0
LEFT = 0
RIGHT = 1


class OculusDrawerCompatibility():

    def __init__(self, caps):
        self.caps = caps
    
    def init_gl(self):
        pass

    def display_rift_left(self):
        _, image = self.caps[LEFT].read()
        self.display_common_gl(image)

    def display_rift_right(self):
        _, image = self.caps[RIGHT].read()
        self.display_common_gl(image)

    def display_common_gl(self, image):
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
            
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

        glEnable(GL_TEXTURE_2D)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, WIDTH, 0, HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(WIDTH, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(WIDTH, HEIGHT)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, HEIGHT)
        glEnd()
    
    def dispose_gl(self):
        pass


class HMDRender():

    def __init__(self, caps):
        self.caps = caps
        self.win_subs = []

        self.renderer = RiftGLRendererCompatibility()
        self.renderer.append(OculusDrawerCompatibility(caps))
        
        ### main window
        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(WIDTH, HEIGHT)
        glutInitWindowPosition(50, 50)
        self.win_main = glutCreateWindow(b"HighSight")
        glutDisplayFunc(self._display)
        glutReshapeFunc(self._reshape)
        glutKeyboardFunc(self._keyboard)

        ### left window(sub window)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(WIDTH / 2, HEIGHT)
        self.win_subs.append(glutCreateSubWindow(self.win_main, 0, 0, WIDTH / 2, HEIGHT))
        glutDisplayFunc(self.renderer[0].display_rift_left)
        glutKeyboardFunc(self._keyboard)

        ### right window(sub window)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        self.win_subs.append(glutCreateSubWindow(self.win_main, WIDTH / 2, 0, WIDTH / 2, HEIGHT))
        glutDisplayFunc(self.renderer[0].display_rift_right)
        glutKeyboardFunc(self._keyboard)

        self.renderer.init_gl()
        self.renderer.rift.recenter_pose()

        glutIdleFunc(self._idle)
        glutMainLoop()

    def _display(self):
        glClearColor(0, 0, 1, 0)
        self.renderer.display_gl()
        glutSwapBuffers()

    def _idle(self):
        for win in self.win_subs:
            glutSetWindow(win)
            glutPostRedisplay()

    def _reshape(self, w, h):
        if h == 0:
            h = 1

        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if w <= h:
            glOrtho(-N_RANGE, N_RANGE, -N_RANGE * h / w, N_RANGE * h / w, -N_RANGE, N_RANGE)
        else:
            glOrtho(-N_RANGE * w / h, N_RANGE * w / h, -N_RANGE, N_RANGE, -N_RANGE, N_RANGE)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
 

    def _keyboard(self, key, x, y):
        if ord(key) == 27:
            if bool(glutLeaveMainLoop):
                glutLeaveMainLoop()
            else:
                raise Exception("Application quit")
        if key == "r":
            self.renderer.rift.recenter_pose()


if __name__ == "__main__":
    caps = []
    caps.append(cv2.VideoCapture(0))
    caps.append(cv2.VideoCapture(0))

    for cap in caps:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    HMDRender(caps)
