#!/bin/env python

import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import sys

sys.path.append("procon28_pyovr/ovr")
from rift_gl_renderer_compatibility import RiftGLRendererCompatibility


WIDTH = 1024 
HEIGHT = 512 
N_RANGE = 1.0

LEFT = 0
RIGHT = 1


class OculusDrawerCompatibility(object):

    def __init__(self, cap):
        self.cap = cap
    
    def init_gl(self):
        glEnable(GL_TEXTURE_2D)
        self.texs = glGenTextures(2)

        _, image = self.cap.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, WIDTH, 0, HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # RIGHT texture
        glBindTexture(GL_TEXTURE_2D, self.texs[RIGHT])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
 
    def idle_gl(self):
        _, image = self.cap.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def display_gl(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0, 0, 1, 0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, WIDTH, 0, HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def resize_gl(self, w, h):
        pass
    
    def dispose_gl(self):
        pass


class EyeLeft(OculusDrawerCompatibility):
    def __init__(self, cap):
        self.cap = cap

    def init_gl(self):
        super(EyeLeft, self).init_gl()

    def idle_gl(self):
        image = super(EyeLeft, self).idle_gl()
        cv2.imshow("left", image)
        # LEFT texture
        glBindTexture(GL_TEXTURE_2D, self.texs[LEFT])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def display_gl(self):
        super(EyeLeft, self).display_gl()      
        glBindTexture(GL_TEXTURE_2D, self.texs[LEFT])
        glPushMatrix()
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, HEIGHT)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(WIDTH, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(WIDTH, HEIGHT)
        glEnd()
        glPopMatrix()
        
        glFlush()

class EyeRight(OculusDrawerCompatibility):
    def __init__(self, cap):
        self.cap = cap

    def init_gl(self):
        super(EyeRight, self).init_gl()

    def idle_gl(self):
        image = super(EyeRight, self).idle_gl()
        cv2.imshow("right", image)
        # RIGHT texture
        glBindTexture(GL_TEXTURE_2D, self.texs[RIGHT])
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
 
    def display_gl(self):
        super(EyeRight, self).display_gl()      
        glBindTexture(GL_TEXTURE_2D, self.texs[RIGHT])
        glPushMatrix()
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, HEIGHT)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(WIDTH, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(WIDTH, HEIGHT)
        glEnd()
        glPopMatrix()

        glFlush()

class HMDRender():

    def __init__(self, cap):
        self.renderer = RiftGLRendererCompatibility()
        self.renderer.append(EyeLeft(cap[LEFT]))
        self.renderer.append(EyeRight(cap[RIGHT]))
        #self.renderer.append(OculusDrawerCompatibility(cap))
        #self.renderer = OculusDrawerCompatibility(cap)
        
        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(WIDTH * 2, HEIGHT)
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
        self.renderer.idle_gl()
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

