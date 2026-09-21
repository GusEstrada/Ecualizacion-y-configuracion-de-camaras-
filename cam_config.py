"""Config minima standalone para las herramientas de camaras.

No depende de BodySense: backend por plataforma y carpeta de evidencias.
"""
import os
import sys

import cv2

BACKEND_CAMARA = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
BASE_REPO = os.path.dirname(os.path.abspath(__file__))
CARPETA_PRUEBAS = os.path.join(BASE_REPO, "pruebas_cam")
