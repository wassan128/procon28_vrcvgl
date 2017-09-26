#!/bin/env python

import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import sys

sys.path.append("procon28_pyovr/ovr")
from rift_gl_renderer_compatibility import RiftGLRendererCompatibility


TEX_WIDTH = 1280 
TEX_HEIGHT = 720 
LEFT = 0
RIGHT = 1

WIN_WIDTH = 300
WIN_HEIGHT = 300 
N_RANGE = 1.0

ESC = 27


class OculusRenderer():
    def __init__(self, cap):
        self.cap = cap
        self.tex = -1

    def _load_image(self):
        _, image = self.cap.read()
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def _resize_image(self, image):
        h = image.shape[0]
        w = image.shape[1]
        return cv2.resize(image, (w, h))
 
    def init_gl(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.0, 0.0, 1.0, 0.0)

        self.tex = glGenTextures(1)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, TEX_WIDTH, 0, TEX_HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        image = self._load_image()
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, TEX_WIDTH, TEX_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
    
    def idle_gl(self):
        try:
            image = self._load_image()
            glBindTexture(GL_TEXTURE_2D, self.tex)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, TEX_WIDTH, TEX_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, image)

        except Exception as e:
            pass

    def display_gl(self):
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, TEX_WIDTH, 0, TEX_HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glEnable(GL_TEXTURE_2D)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, TEX_HEIGHT)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(TEX_WIDTH, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(TEX_WIDTH, TEX_HEIGHT)
        glEnd()

        glFlush()
        glutSwapBuffers()

    def dispose_gl(self):
        pass


class HMDRender():

    def __init__(self, caps):
        self.renderer = RiftGLRendererCompatibility()
        self.renderer.append(OculusRenderer(caps[LEFT]))
        self.renderer.append(OculusRenderer(caps[RIGHT]))

        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(WIN_WIDTH * 2, WIN_HEIGHT)
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
   
    def idle(self):
        self.renderer.idle_gl()
        glutPostRedisplay()

    def resize(self, w, h):
        self.renderer.resize_gl(w, h)

    def key_press(self, key, x, y):
        if ord(key) == ESC:
            if bool(glutLeaveMainLoop):
                glutLeaveMainLoop()
            else:
                raise Exception("Application quit")
        if key == "r":
            self.renderer.rift.recenter_pose()

def main():
    caps = []
    caps.append(cv2.VideoCapture("test3.mp4"))
    caps.append(cv2.VideoCapture("test4.mp4"))
    
    for cap in caps:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, TEX_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TEX_HEIGHT)

    HMDRender(caps)


if __name__ == "__main__":
    main()

