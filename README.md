# Ecualización y configuración de cámaras

Herramientas para dejar las webcams a punto antes de usar BodySense.
Si la imagen está oscura, quemada o una cámara no abre, se diagnostica y se
ajusta aquí, no en el programa principal.

Autor: Gustavo Estrada — 21 sep 2026

## Requisitos

```
pip install opencv-contrib-python numpy pygame
```

## El bueno: `test_cam_controls.py`

```
python test_cam_controls.py
```

Este es el programa que realmente se usa. Abre las dos cámaras en vivo y
permite ajustar Exposure, Brightness y Contrast con valores numéricos
(click en el valor, escribes el número y Enter). Cada cambio se aplica al
instante y se muestra el valor real que devuelve el driver.

Debajo de cada cámara hay un histograma de color en vivo con el porcentaje
de negro y quemado, así el ajuste se hace con números y no a ojo. Cuando la
imagen queda bien, el botón **Tomar foto** guarda la evidencia en
`pruebas_cam/`: `prueba_N.png` (ambas cámaras lado a lado con histogramas) y
`prueba_N.txt` (fecha, parámetros usados y porcentajes del histograma).

El programa arranca con los valores que trae cada cámara y prueba los
backends DSHOW, ANY y MSMF solo. No fuerza nada al abrir.

## El detective: `diagnostico_cam.py`

```
python diagnostico_cam.py
```

Cuando una cámara no se ve, este script dice por qué. Prueba los índices 0-3
con los tres backends sin modificar nada y reporta por cada combinación si
abre, el tamaño de cuadro y el brillo medio.

Así se distingue un problema de índice o backend (no abre) de un shutter
físico cerrado, un permiso de Windows o un driver atorado (abre pero da
negro, brillo 0.0). Guarda foto de la mejor combinación en
`diagnostico_cam<N>.png`.

Nota: cerrar Teams, Zoom y el navegador antes de correrlo, la cámara es de
uso exclusivo en Windows.

## Archivos que se generan

- `pruebas_cam/prueba_N.png` + `.txt` — evidencias del ajuste.
- `diagnostico_cam<N>.png` — foto del diagnóstico (ignorada por git).
