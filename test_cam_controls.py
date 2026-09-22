"""Ajuste de camaras BodySense V1: dos camaras + panel lateral numerico.

Ventana pygame con la misma colorimetria del menu (marfil/blanco/vino).
Click en un valor, escribe el numero y Enter para aplicarlo en vivo.
ESC para salir.

    python3 test_cam_controls.py
"""
import os
import sys
import time

import cv2
import numpy as np
import pygame

try:
    from cam_config import BACKEND_CAMARA, CARPETA_PRUEBAS
except ImportError:
    BACKEND_CAMARA = cv2.CAP_DSHOW
    CARPETA_PRUEBAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruebas_cam")

# --- tema menu ---
FONDO = (244, 241, 235)
TARJETA = (255, 255, 255)
BORDE = (225, 218, 208)
TINTA = (62, 32, 32)
TINTA_SUAVE = (130, 110, 110)
TINTA_TENUE = (170, 155, 150)
ACENTO = (122, 30, 35)
ACENTO_CLARO = (150, 45, 50)
VERDE = (63, 160, 120)
ROJO = (190, 70, 60)

FAM_TITULO = "georgia,timesnewroman,times,serif"
FAM = "segoeui,helveticaneue,helvetica,arial,dejavusans"
FAM_MONO = "menlo,consolas,dejavusansmono,couriernew,monospace"

ANCHO, ALTO = 1280, 760
BARRA_LAT = 330
VW, VH = 452, 339  # cada vista de camara

# Indices reales: la integrada es la 1 y se esquiva.
CAMS = (0, 2)

PROPS = [
    ("Exposure", cv2.CAP_PROP_EXPOSURE, -13.0, 0.0, -4.0, 1.0),
    ("Brightness", cv2.CAP_PROP_BRIGHTNESS, -100.0, 100.0, 0.0, 5.0),
    ("Contrast", cv2.CAP_PROP_CONTRAST, 0.0, 100.0, 50.0, 5.0),
]


class Campo:
    def __init__(self, cap_idx, nombre, prop, minimo, maximo, default, paso):
        self.cap_idx = cap_idx
        self.nombre = nombre
        self.prop = prop
        self.minimo = minimo
        self.maximo = maximo
        self.paso = paso
        self.texto = str(default)
        self.editando = False
        self.leido = None

    def recortar(self, v):
        return min(self.maximo, max(self.minimo, v))

    def aplicar(self, caps, mensajes):
        try:
            v = float(self.texto)
        except ValueError:
            mensajes.append(f"cam{CAMS[self.cap_idx]} {self.nombre}: '{self.texto}' no es numero")
            return
        v = self.recortar(v)
        self.texto = str(round(v, 3))
        cap = caps[self.cap_idx]
        if cap is not None and cap.isOpened():
            cap.set(self.prop, v)
            self.leido = cap.get(self.prop)
        else:
            mensajes.append(f"cam{CAMS[self.cap_idx]} no responde")


def abrir_cam(idx):
    for backend in (BACKEND_CAMARA, cv2.CAP_ANY, getattr(cv2, "CAP_MSMF", cv2.CAP_ANY)):
        try:
            cap = cv2.VideoCapture(idx, backend)
        except Exception:
            continue
        if cap is not None and cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            # Calentamiento: los primeros cuadros suelen salir negros.
            for _ in range(5):
                cap.read()
            return cap
        if cap is not None:
            cap.release()
    return None


def aplicar_defaults(caps, campos):
    for c in campos:
        c.texto = str(next(p[4] for p in PROPS if p[1] == c.prop))
    for c in campos:
        try:
            caps[c.cap_idx].set(c.prop, float(c.texto))
            c.leido = caps[c.cap_idx].get(c.prop)
        except (AttributeError, TypeError):
            pass


def hist_strip(frame, w=640, h=90):
    """Tira de histograma BGR + % aplastado/quemado. Devuelve (tira, negro%, quemado%)."""
    chica = cv2.resize(frame, (320, 240))
    gris = cv2.cvtColor(chica, cv2.COLOR_BGR2GRAY)
    total = gris.size
    negro = float(np.mean(gris <= 5)) * 100.0
    quemado = float(np.mean(gris >= 250)) * 100.0
    tira = np.full((h, w, 3), 255, np.uint8)
    for ch, color in ((0, (200, 60, 60)), (1, (60, 160, 60)), (2, (60, 60, 200))):
        hist = cv2.calcHist([chica], [ch], None, [64], [0, 256])
        cv2.normalize(hist, hist, 0, h - 28, cv2.NORM_MINMAX)
        pts = np.column_stack((np.linspace(0, w - 1, 64), h - 8 - hist.ravel())).astype(np.int32)
        cv2.polylines(tira, [pts], False, color, 2)
    cv2.putText(tira, f"negro {negro:.1f}%  quemado {quemado:.1f}%",
                (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (62, 32, 32), 1)
    return tira, negro, quemado


def siguiente_indice():
    os.makedirs(CARPETA_PRUEBAS, exist_ok=True)
    n = 0
    for f in os.listdir(CARPETA_PRUEBAS):
        if f.startswith("prueba_") and f.endswith(".png"):
            try:
                n = max(n, int(f[len("prueba_"):-len(".png")]))
            except ValueError:
                pass
    return n + 1


def tomar_foto(frames, campos):
    """Guarda cam0 y cam1 lado a lado + txt con los parametros. Devuelve ruta."""
    n = siguiente_indice()
    vistas = []
    stats = []
    for i in (0, 1):
        fr = frames[i]
        if fr is None:
            fr = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(fr, f"cam{CAMS[i]}: sin senal", (20, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            tira = np.full((90, 640, 3), 255, np.uint8)
            cv2.putText(tira, "sin histograma", (8, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (62, 32, 32), 1)
            stats.append((0.0, 0.0))
        else:
            cv2.putText(fr, f"cam{CAMS[i]}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            tira, negro, quemado = hist_strip(fr)
            stats.append((negro, quemado))
        vistas.append(cv2.vconcat([cv2.resize(fr, (640, 480)), tira]))
    panel = cv2.hconcat(vistas)
    ruta = os.path.join(CARPETA_PRUEBAS, f"prueba_{n}.png")
    cv2.imwrite(ruta, panel)
    lineas = [f"prueba_{n}  {time.strftime('%Y-%m-%d %H:%M:%S')}"]
    for i, (negro, quemado) in enumerate(stats):
        lineas.append(f"cam{CAMS[i]} histograma: negro {negro:.1f}%  quemado {quemado:.1f}%")
    for c in campos:
        lineas.append(f"cam{CAMS[c.cap_idx]} {c.nombre}: pedido {c.texto}  real {c.leido}")
    with open(os.path.join(CARPETA_PRUEBAS, f"prueba_{n}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    return ruta


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("BodySense V1 - Ajuste de camaras")
    reloj = pygame.time.Clock()
    f_titulo = pygame.font.SysFont(FAM_TITULO, 30, bold=True)
    f_sec = pygame.font.SysFont(FAM, 16, bold=True)
    f = pygame.font.SysFont(FAM, 13)
    f_bold = pygame.font.SysFont(FAM, 13, bold=True)
    f_chico = pygame.font.SysFont(FAM, 11)
    mono = pygame.font.SysFont(FAM_MONO, 13)

    caps = [abrir_cam(c) for c in CAMS]
    # No fuerzo Exposure/Brightness/Contrast al abrir: en la integrada
    # un exposure agresivo la deja negra. Se leen los valores del driver.

    campos = []
    for idx in (0, 1):
        for nombre, prop, minimo, maximo, default, paso in PROPS:
            campos.append(Campo(idx, nombre, prop, minimo, maximo, default, paso))
    for c in campos:
        cap = caps[c.cap_idx]
        if cap is not None:
            c.leido = cap.get(c.prop)
            # El campo arranca con lo que trae el driver, no con mi default.
            try:
                v = float(c.leido)
                if v == v and c.minimo - 1e-6 <= v <= c.maximo + 1e-6:
                    c.texto = str(round(v, 3))
            except (TypeError, ValueError):
                pass

    mensajes = []
    andando = True
    ultimos = [None, None]
    while andando:
        click = None
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                andando = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                edit = next((c for c in campos if c.editando), None)
                if edit:
                    edit.editando = False
                else:
                    andando = False
            elif ev.type == pygame.KEYDOWN and any(c.editando for c in campos):
                c = next(c for c in campos if c.editando)
                if ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                    c.editando = False
                    c.aplicar(caps, mensajes)
                elif ev.key == pygame.K_BACKSPACE:
                    c.texto = c.texto[:-1]
                elif ev.unicode and len(c.texto) < 10 and (ev.unicode.isdigit() or ev.unicode in "-."):
                    c.texto += ev.unicode
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                click = ev.pos

        mouse = pygame.mouse.get_pos()
        pantalla.fill(FONDO)
        pantalla.blit(f_titulo.render("BodySense V1", True, TINTA), (24, 10))
        pantalla.blit(f.render("Ajuste de camaras: escribe el valor y Enter. ESC sale.",
                               True, TINTA_SUAVE), (24, 48))

        # --- vistas ---
        for i, (cx0) in enumerate((24, 24 + VW + 14)):
            cap = caps[i]
            ok, frame = (False, None)
            if cap is not None and cap.isOpened():
                ok, frame = cap.read()
            if ok and frame is not None:
                ultimos[i] = frame.copy()
            area = pygame.Rect(cx0, 80, VW, VH)
            pygame.draw.rect(pantalla, TARJETA, area, border_radius=10)
            pygame.draw.rect(pantalla, BORDE, area, 1, border_radius=10)
            if ok and frame is not None:
                brillo = float(np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))
                rgb = cv2.cvtColor(cv2.resize(frame, (VW, VH)), cv2.COLOR_BGR2RGB)
                surf = pygame.image.frombuffer(rgb.tobytes(), (VW, VH), "RGB")
                pantalla.blit(surf, (cx0, 80))
                tira, negro, quemado = hist_strip(frame, VW, 76)
                tsurf = pygame.image.frombuffer(cv2.cvtColor(tira, cv2.COLOR_BGR2RGB).tobytes(),
                                                (VW, 76), "RGB")
                pantalla.blit(tsurf, (cx0, 80 + VH + 4))
                if brillo < 5:
                    pantalla.blit(f.render("imagen negra: sube Exposure o Brightness",
                                           True, ROJO), (cx0 + 12, 80 + VH + 84))
                elif quemado > 10:
                    pantalla.blit(f.render(f"quemada {quemado:.0f}%: baja Exposure",
                                           True, ROJO), (cx0 + 12, 80 + VH + 84))
            else:
                pantalla.blit(f.render(f"cam{CAMS[i]}: NO responde", True, ROJO), (cx0 + 20, 80 + VH // 2))
            etiqueta = f"cam{CAMS[i]}: {'OK' if ok else 'sin senal'}"
            pygame.draw.rect(pantalla, (0, 0, 0), (cx0 + 8, 86, 150, 22), border_radius=5)
            pantalla.blit(f_bold.render(etiqueta, True, (0, 255, 0) if ok else (0, 0, 255)),
                          (cx0 + 14, 89))

        # --- barra lateral ---
        bx = ANCHO - BARRA_LAT
        pygame.draw.rect(pantalla, TARJETA, (bx, 0, BARRA_LAT, ALTO), border_radius=0)
        pygame.draw.line(pantalla, BORDE, (bx, 0), (bx, ALTO), 1)
        pantalla.blit(f_sec.render("Valores", True, TINTA), (bx + 20, 16))

        y = 48
        for idx in (0, 1):
            pantalla.blit(f_sec.render(f"CAM {CAMS[idx]}", True, TINTA), (bx + 20, y))
            y += 26
            for c in [c for c in campos if c.cap_idx == idx]:
                pantalla.blit(f.render(c.nombre, True, TINTA_SUAVE), (bx + 20, y + 5))
                caja = pygame.Rect(bx + 120, y, 90, 26)
                pygame.draw.rect(pantalla, (36, 48, 62) if False else (FONDO if not c.editando else (255, 255, 255)),
                                 caja, border_radius=6)
                pygame.draw.rect(pantalla, ACENTO if c.editando else BORDE, caja, 1, border_radius=6)
                pantalla.blit(mono.render(c.texto or "0", True, TINTA), (bx + 128, y + 5))
                rm = pygame.Rect(bx + 214, y, 26, 26)
                rp = pygame.Rect(bx + 242, y, 26, 26)
                for r, t in ((rm, "-"), (rp, "+")):
                    enc = r.collidepoint(mouse)
                    pygame.draw.rect(pantalla, (250, 246, 240) if enc else (235, 228, 218),
                                     r, border_radius=6)
                    pygame.draw.rect(pantalla, BORDE, r, 1, border_radius=6)
                    pantalla.blit(f_bold.render(t, True, TINTA), f_bold.render(t, True, TINTA).get_rect(center=r.center))
                if click:
                    if caja.collidepoint(click):
                        for o in campos:
                            o.editando = False
                        c.editando = True
                    elif rm.collidepoint(click):
                        try:
                            c.texto = str(round(c.recortar(float(c.texto or 0) - c.paso), 3))
                        except ValueError:
                            pass
                        c.editando = False
                        c.aplicar(caps, mensajes)
                    elif rp.collidepoint(click):
                        try:
                            c.texto = str(round(c.recortar(float(c.texto or 0) + c.paso), 3))
                        except ValueError:
                            pass
                        c.editando = False
                        c.aplicar(caps, mensajes)
                leido = f"{c.leido:.2f}" if c.leido is not None else "--"
                pantalla.blit(f_chico.render(f"real {leido}  [{c.minimo:g}..{c.maximo:g}]",
                                             True, TINTA_TENUE), (bx + 20, y + 28))
                y += 52
            y += 8

        rdef = pygame.Rect(bx + 20, y, BARRA_LAT - 40, 36)
        enc = rdef.collidepoint(mouse)
        pygame.draw.rect(pantalla, ACENTO_CLARO if enc else ACENTO, rdef, border_radius=8)
        pantalla.blit(f_bold.render("Restablecer", True, (255, 255, 255)),
                      f_bold.render("Restablecer", True, (255, 255, 255)).get_rect(center=rdef.center))
        if click and rdef.collidepoint(click):
            aplicar_defaults(caps, campos)
            mensajes.append("Valores por defecto aplicados")

        rfoto = pygame.Rect(bx + 20, y + 44, BARRA_LAT - 40, 40)
        encf = rfoto.collidepoint(mouse)
        pygame.draw.rect(pantalla, (250, 246, 240) if encf else (235, 228, 218),
                         rfoto, border_radius=8)
        pygame.draw.rect(pantalla, ACENTO, rfoto, 1, border_radius=8)
        pantalla.blit(f_bold.render("Tomar foto", True, TINTA),
                      f_bold.render("Tomar foto", True, TINTA).get_rect(center=rfoto.center))
        if click and rfoto.collidepoint(click):
            try:
                ruta = tomar_foto(ultimos, campos)
                mensajes.append(f"Guardada {os.path.basename(ruta)} con sus parametros")
            except OSError as e:
                mensajes.append(f"No se pudo guardar: {e}")

        if mensajes:
            pantalla.blit(f_chico.render(mensajes[-1][:90], True, ROJO), (24, ALTO - 26))

        pygame.display.flip()
        reloj.tick(30)

    for cap in caps:
        if cap is not None:
            cap.release()
    pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
