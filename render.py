import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys

# for oculus compatibility
from ovr.rift_gl_renderer_compatibility import RiftGLRendererCompatibility
from ovr.oculus_drawer_compatibility import OculusDrawerCompatibility

# consts
WIDTH = 640
HEIGHT = 480
N_RANGE = 1.0
ESC = 27


class HMDRender():

    def __init__(self, capture):
        self.capture = capture

        self.renderer = RiftGLRendererCompatibility()
        self.renderer.append(OculusDrawerCompatibility(WIDTH, HEIGHT))

        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(WIDTH, HEIGHT)
        glutInitWindowPosition(WIDTH - WIDTH / 2, HEIGHT - HEIGHT / 2)
        glutCreateWindow(b"OpenGL + OpenCV")

        glClearColor(0.0, 0.0, 0.0, 1.0)

        glutDisplayFunc(self._display)
        glutReshapeFunc(self._reshape)
        glutKeyboardFunc(self._keyboard)
        glutIdleFunc(self._idle)

        self.renderer.init_gl()
        self.renderer.rift.recenter_pose()

        glutMainLoop()


    # glutIdleFunc
    def _idle(self):
        _, image = self.capture.read()

        cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
        self.display_gl(image)
        glutPostRedisplay()


    # glutDisplayFunc
    def _display(self):
        self.renderer.display_gl(self.capture)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_TEXTURE_2D)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, WIDTH, 0, HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glFlush()
        glutSwapBuffers()


    # glutReshapeFunc
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


    # glutKeyboardFunc
    def _keyboard(self, key, x, y):
        if key == chr(ESC):
            sys.exit()


### main function ###
def main():
    capture = cv2.VideoCapture(0)
    
    # settings of capture frame
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    
    HMDRender(capture) 


if __name__ == "__main__":
    main()

