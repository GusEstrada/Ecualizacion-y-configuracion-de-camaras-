# Ecualización y configuración de cámaras

Herramientas para ajuste y diagnóstico de webcams USB (Windows + OpenCV).

Autor: Gustavo Estrada — 21 sep 2026

## Requisitos

```
pip install opencv-contrib-python numpy pygame
```

## Scripts

### `test_cam_controls.py` — panel de ajuste doble cámara

```
python test_cam_controls.py
```

Ventana pygame con el tema BodySense V1 (marfil/blanco/vino). Muestra cam0 y
cam1 en vivo, lado a lado, con su estado (OK / sin señal).

- **Barra lateral con valores numéricos** de Exposure, Brightness y Contrast
  por cámara: click en el valor, escribes el número y Enter para aplicarlo en
  vivo. Botones −/+ y lectura del valor real que devuelve el driver.
- **Histograma BGR en vivo** debajo de cada cámara (`cv2.calcHist`) con
  porcentaje de negro (≤5) y quemado (≥250). Avisos: imagen negra (sube
  Exposure/Brightness) y quemada >10% (baja Exposure).
- **Botón Tomar foto**: guarda `pruebas_cam/prueba_N.png` (ambas cámaras lado
  a lado con histogramas) + `prueba_N.txt` (fecha, parámetros pedidos/reales
  e histograma). El índice arranca en 1 y continúa del último existente.
- **Botón Restablecer**: vuelve a Exposure −4, Brightness 0, Contrast 50.
- ESC para salir.

Al abrir no fuerza valores: arranca con los del driver y prueba backends
DSHOW → ANY → MSMF, con calentamiento de 5 cuadros.

### `diagnostico_cam.py` — escáner de cámaras

```
python diagnostico_cam.py
```

Prueba índices 0-3 con backends ANY/MSMF/DSHOW sin forzar resolución ni
exposición. Reporta por combinación si abre, tamaño de cuadro y brillo medio.
Guarda foto de la mejor (`diagnostico_cam<N>.png`).

Útil cuando una cámara abre pero da negro (brillo 0.0): distingue problema de
índice/backend (no abre) de shutter físico, permiso de Windows o driver
(abre pero negro). Cierra Teams/Zoom/navegador antes de correrlo, la cámara
es exclusiva en Windows.

### `ver_cam_control.py` — visor simple (legacy)

```
python ver_cam_control.py
```

Una sola cámara (índice 1) con trackbars de OpenCV para Exposure/Brightness/
Contrast. Versión anterior al panel numérico; se conserva de referencia.

## Archivos que genera

- `pruebas_cam/prueba_N.png` + `.txt` — evidencias del ajuste.
- `diagnostico_cam<N>.png` — foto del diagnóstico (ignorada por git).
