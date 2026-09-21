import cv2

WINDOW = "Camera Live Controls"
CAM_INDEX = 1
BACKEND = cv2.CAP_DSHOW


PROPS = {
    "Exposure": cv2.CAP_PROP_EXPOSURE,
    "Brightness": cv2.CAP_PROP_BRIGHTNESS,
    "Contrast": cv2.CAP_PROP_CONTRAST,
}

RANGOS = {
    cv2.CAP_PROP_EXPOSURE: (-13.0, 0.0),
    cv2.CAP_PROP_BRIGHTNESS: (-100.0, 100.0),
    cv2.CAP_PROP_CONTRAST: (0.0, 100.0),
}

DEFAULTS = {
    cv2.CAP_PROP_EXPOSURE: -4.0,
    cv2.CAP_PROP_BRIGHTNESS: 0.0,
    cv2.CAP_PROP_CONTRAST: 50.0,
}


def valor_a_pos(valor, minimo, maximo):
    if maximo == minimo:
        return 0
    return int(round(100 * (valor - minimo) / (maximo - minimo)))


def pos_a_valor(pos, minimo, maximo):
    return minimo + (maximo - minimo) * pos / 100.0


cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
for nombre, prop in PROPS.items():
    default = DEFAULTS[prop]
    minimo, maximo = RANGOS[prop]
    inicio = valor_a_pos(default, minimo, maximo)
    cv2.createTrackbar(nombre, WINDOW, inicio, 100, lambda *_: None)

cap = cv2.VideoCapture(CAM_INDEX, BACKEND)
if not cap.isOpened():
    raise RuntimeError(f"No se pudo abrir la camara {CAM_INDEX}")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)
cap.set(cv2.CAP_PROP_EXPOSURE, -4.0)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.0)
cap.set(cv2.CAP_PROP_CONTRAST, 50.0)

print("La camara esta abierta. Mueve solo Exposure/Brightness/Contrast.")
print("ESC para salir.")

while True:
    ok, frame = cap.read()
    if not ok:
        print("No se pudo leer frame.")
        break

    for i, (nombre, prop) in enumerate(PROPS.items()):
        pos = cv2.getTrackbarPos(nombre, WINDOW)
        minimo, maximo = RANGOS[prop]
        valor = pos_a_valor(pos, minimo, maximo)
        cap.set(prop, valor)
        leido = cap.get(prop)
        cv2.putText(frame, f"{nombre}: {leido:.3f}",
                    (10, 28 + 25 * i),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.imshow(WINDOW, frame)
    key = cv2.waitKey(30) & 0xFF
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
