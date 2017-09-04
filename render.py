import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys


# setup of window 
WIDTH = 640
HEIGHT = 480 
N_RANGE = 1.0

# global variable
global capture
capture = None


# Functions initialize for OpenGL
def init():
    glClearColor(0.0, 0.0, 0.0, 1.0) # rgba

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)


# glutIdleFunc
def idle():
    global capture
    _, image = capture.read()
    
    glTexImage2D(GL_TEXTURE_2D,
            0,
            GL_RGB,
            WIDTH, HEIGHT,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            image)
    glutPostRedisplay()


# glutDisplayFunc
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
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

    glFlush()
    glutSwapBuffers()


# glutReshapeFunc
def reshape(w, h):
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


# glutKeyboardFunc
def keyboard(key, x, y):
    if key == chr(27):
        sys.exit()


### main function ###
def main():
    global capture
    capture = cv2.VideoCapture(0)
    
    # settings of capture frame
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(WIDTH - WIDTH / 2, HEIGHT - HEIGHT / 2)
    glutCreateWindow(b"OpenGL + OpenCV")

    init()
    glutMainLoop()


if __name__ == "__main__":
    main()

