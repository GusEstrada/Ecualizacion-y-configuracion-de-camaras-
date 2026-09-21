# Ecualización y configuración de cámaras

Herramientas para ajuste y diagnóstico de webcams USB (Windows + OpenCV).

Autor: Gustavo Estrada — 21 sep 2026

## Scripts

- `test_cam_controls.py` — panel pygame doble cámara con valores numéricos,
  histograma BGR en vivo y botón Tomar foto (`pruebas_cam/prueba_N.png + .txt`).
- `diagnostico_cam.py` — escanea índices 0-3 con backends ANY/MSMF/DSHOW y
  reporta brillo medio. Útil cuando una cámara abre pero da negro.
- `ver_cam_control.py` — visor simple legacy de una cámara.

## Uso

```
pip install opencv-contrib-python numpy pygame
python test_cam_controls.py
python diagnostico_cam.py
```
