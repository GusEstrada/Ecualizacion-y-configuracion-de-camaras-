"""Diagnostico de camaras: prueba indices 0-3 con varios backends sin forzar nada.

    python3 diagnostico_cam.py

Imprime brillo medio por combinacion y guarda foto de la mejor en
diagnostico_cam<N>.png para que la veas.
"""
import cv2
import numpy as np

BACKENDS = [
    ("ANY", cv2.CAP_ANY),
    ("MSMF", getattr(cv2, "CAP_MSMF", cv2.CAP_ANY)),
    ("DSHOW", getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY)),
]

print("Cierra Teams/Zoom/navegador antes: en Windows la camara es exclusiva.")
print("Revisa el shutter fisico de la HP y Privacidad > Camara.\n")

mejor = None
for idx in range(4):
    for nombre_b, backend in BACKENDS:
        cap = cv2.VideoCapture(idx, backend)
        if not cap.isOpened():
            print(f"cam{idx} {nombre_b}: no abre")
            cap.release()
            continue
        # Sin forzar resolucion ni exposicion: leo lo que da el driver.
        brillo, forma, ok_final = None, None, False
        for _ in range(30):
            ok, frame = cap.read()
            if ok and frame is not None:
                ok_final = True
                forma = f"{frame.shape[1]}x{frame.shape[0]}"
                brillo = float(np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))
        estado = f"abre, cuadro {forma}, brillo {brillo:.1f}" if ok_final else "abre pero NO da cuadros"
        print(f"cam{idx} {nombre_b}: {estado}")
        if ok_final and brillo is not None and (mejor is None or brillo > mejor[0]):
            mejor = (brillo, idx, nombre_b, frame)
        cap.release()

print()
if mejor and mejor[0] > 5:
    brillo, idx, nombre_b, frame = mejor
    ruta = f"diagnostico_cam{idx}.png"
    cv2.imwrite(ruta, frame)
    print(f"Mejor: cam{idx} con {nombre_b} (brillo {brillo:.1f}). Foto guardada en {ruta}, abrela.")
else:
    print("Ninguna combinacion dio imagen con luz. Revisa shutter fisico,")
    print("permiso de Windows y que ninguna app tenga la camara abierta.")
