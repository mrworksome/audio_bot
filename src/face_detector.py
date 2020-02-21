import os
import cv2


class FaceDetector(object):
    def __init__(self):
        path = os.path.join(cv2.__path__[0], 'data/haarcascade_frontalface_alt.xml')
        self.haar_face_cascade = cv2.CascadeClassifier(path)

    def detect_faces(self, path_file: str, scale_factor=1.1):
        bgr_img = cv2.imread(path_file)
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)  # need grayscale image

        # detect faces
        faces = self.haar_face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=5
        )

        if len(faces) != 0:
            return True
        return False

