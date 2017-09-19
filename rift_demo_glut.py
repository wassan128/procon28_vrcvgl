#!/bin/env python

import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import sys

sys.path.append("procon28_pyovr/ovr")
from rift_gl_renderer_compatibility import RiftGLRendererCompatibility


WIDTH = 1280 / 2
HEIGHT = 720 / 2
N_RANGE = 1.0

LEFT = 0
RIGHT = 1

class OculusDrawerCompatibility():

    def __init__(self, caps):
        self.caps = caps
    
    def init_gl(self):
        self.texs = glGenTextures(2)

    def display_gl(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0, 0, 1, 0)

        images = []
        for eye in range(2):
            _, images = self.caps[eye].read()
            cv2.cvtColor(images, cv2.COLOR_BGR2RGB, images[eye])

        # LEFT texture        
        glEnable(GL_TEXTURE_2D)
    
        glBindTexture(GL_TEXTURE_2D, self.texs[LEFT])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

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

        # RIGHT texture        
        glBindTexture(GL_TEXTURE_2D, self.texs[RIGHT])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, image_right)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

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

        glFlush()

    def resize_gl(self, w, h):
        pass
        """
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

        glutSwapBuffers()
        """

        
    
    def dispose_gl(self):
        pass


class HMDRender():

    def __init__(self, caps):
        self.renderer = RiftGLRendererCompatibility()
        self.renderer.append(OculusDrawerCompatibility(caps))
        #self.renderer = OculusDrawerCompatibility(caps)
        
        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(WIDTH, HEIGHT)
        glutInitWindowPosition(50, 50)
        win = glutCreateWindow(b"HighSight")

        glutDisplayFunc(self.display)
        glutIdleFunc(self.idle)
        glutReshapeFunc(self.renderer.resize_gl)
        glutKeyboardFunc(self.key_press)

        self.renderer.init_gl()
        self.renderer.rift.recenter_pose()

        glutMainLoop()

    def display(self):
        self.renderer.display_gl()
        glutSwapBuffers()
   
    def idle(self):
        glutPostRedisplay()

    def resize(self, w, h):
        self.renderer.resize_gl(w, h)

    def key_press(self, key, x, y):
        if ord(key) == 27:
            if bool(glutLeaveMainLoop):
                glutLeaveMainLoop()
            else:
                raise Exception("Application quit")
        if key == "r":
            self.renderer.rift.recenter_pose()

def main():
    caps = []
    caps.append(cv2.VideoCapture(0))
    caps.append(cv2.VideoCapture(0))

    for cap in caps:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    HMDRender(caps)


if __name__ == "__main__":
    main()

