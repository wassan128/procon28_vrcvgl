#!/bin/env python

import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import sys

sys.path.append("pyovr/ovr")
from rift_gl_renderer_compatibility import RiftGLRendererCompatibility


WIDTH = 640 
HEIGHT = 480 

class OculusDrawerCompatibility():
    
    def init_gl(self):
        pass

    def display_gl(self):
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(WIDTH, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(WIDTH, HEIGHT)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, HEIGHT)
        glEnd()

    def idle_gl(self, image):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_TEXTURE_2D)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, WIDTH, 0, HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glutPostRedisplay()
	
        glFlush()
        glutSwapBuffers()


    def dispose_gl(self):
        pass


class GlutDemoApp():

    def __init__(self, cap):
        self.cap = cap
        self.renderer = RiftGLRendererCompatibility()
        self.renderer.append(OculusDrawerCompatibility())

        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(WIDTH, HEIGHT)
        glutInitWindowPosition(50, 50)
        win = glutCreateWindow(b"Just a triangle")

        glutDisplayFunc(self.display)
        glutIdleFunc(self.idle)
        glutReshapeFunc(self.renderer.resize_gl)
        glutKeyboardFunc(self.key_press)
        self.renderer.init_gl()
        self.renderer.rift.recenter_pose()
        glutMainLoop()

    def idle(self):
        _, image = self.cap.read()
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
        self.renderer[0].idle_gl(image)

    def display(self):
        self.renderer.display_gl()
        glutSwapBuffers()

    def key_press(self, key, x, y):
        if ord(key) == 27:
            # print "Escape!"
            if bool(glutLeaveMainLoop):
                glutLeaveMainLoop()
            else:
                raise Exception("Application quit")
        if key == "r":
            self.renderer.rift.recenter_pose()


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    GlutDemoApp(cap)
