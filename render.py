import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys

# for oculus compatibility
from ovr.rift_gl_renderer_compatibility import RiftGLRendererCompatibility

# consts
WIDTH = 640 
HEIGHT = 320 
N_RANGE = 1.0
ESC = 27
LEFT = 0
RIGHT = 1


class OculusDrawerCompatibility():

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def init_gl(self):
        pass

    def display_gl(self):
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(width, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(self.width, self.height)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, self.height)
        glEnd()

    
class HMDRender():

    def __init__(self, caps):
        self.caps = caps
        self.win_subs = []

        self.renderer = RiftGLRendererCompatibility()
        self.renderer.append(OculusDrawerCompatibility(WIDTH, HEIGHT))

        glutInit(sys.argv)
        
        ### main window
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(WIDTH, HEIGHT)
        glutInitWindowPosition(WIDTH - WIDTH / 2, HEIGHT - HEIGHT / 2)
        self.win_main = glutCreateWindow(b"HighSight")
        glutDisplayFunc(self._display)
        glutReshapeFunc(self._reshape)
        glutKeyboardFunc(self._keyboard)

        ### left window(sub window)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(WIDTH / 2, HEIGHT)
        self.win_subs.append(glutCreateSubWindow(self.win_main, 0, 0, WIDTH / 2, HEIGHT))
        glutDisplayFunc(self._display_left)
        glutKeyboardFunc(self._keyboard)

        ### right window(sub window)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(WIDTH / 2, HEIGHT)
        self.win_subs.append(glutCreateSubWindow(self.win_main, WIDTH / 2, 0, WIDTH / 2, HEIGHT))
        glutDisplayFunc(self._display_right)
        glutKeyboardFunc(self._keyboard)


        self.renderer.init_gl()
        self.renderer.rift.recenter_pose()

        glutIdleFunc(self._idle)
        glutMainLoop()


    ### glutIdleFunc
    def _idle(self):
        for win in self.win_subs:
            glutSetWindow(win)
            glutPostRedisplay()


    ### main window glutDisplayFunc
    def _display(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    ### left window glutDisplayFunc
    def _display_left(self):
        _, image = self.caps[LEFT].read()
        self._display_common(image)


    ### right window glutDisplayFunc
    def _display_right(self):
        _, image = self.caps[RIGHT].read()
        self._display_common(image)


    ### common(right and left) window glutDisplayFunc
    def _display_common(self, image):
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

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


    ### glutReshapeFunc
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


    ### glutKeyboardFunc
    def _keyboard(self, key, x, y):
        if key == chr(ESC):
            sys.exit()


### main function ###
def main():
    caps = []
    caps.append(cv2.VideoCapture(0))
    caps.append(cv2.VideoCapture(0))

    ### settings of capture frame
    for cap in caps:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    HMDRender(caps)

    ### release
    for cap in caps:
        cap.release()

if __name__ == "__main__":
    main()

