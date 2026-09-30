import pygame
import random
import sys
import json
import os
import math
import array
import copy

# --- CONFIGURACIÓN DE RESOLUCIÓN VIRTUAL Y PANTALLA ---
ANCHO_VIRTUAL, ALTO_VIRTUAL = 520, 840  # Resolución fija interna
TAMANO_CELDA = 45
MARGEN = 5
ANCHO_TABLERO = 8 * (TAMANO_CELDA + MARGEN) + MARGEN
POS_TABLERO_X = (ANCHO_VIRTUAL - ANCHO_TABLERO) // 2 + 20
POS_TABLERO_Y = 140

# Colores (RGB)
COLOR_FONDO = (15, 18, 26)
COLOR_TABLERO = (25, 32, 45)
COLOR_CASILLA_VACIA = (32, 42, 58)
COLOR_TEXTO = (240, 240, 240)
COLOR_DORADO = (255, 215, 0)
COLOR_BOTON = (38, 48, 66)

COLORES_PIEZAS = [
    (239, 68, 68),   # Rojo
    (59, 130, 246),  # Azul
    (34, 197, 94),   # Verde
    (234, 179, 8),   # Amarillo
    (168, 85, 247),  # Morado
    (236, 72, 153),  # Rosa
    (20, 184, 166)   # Turquesa
]

FORMAS = [
    [(0,0)],
    [(0,0), (1,0)],
    [(0,0), (0,1)],
    [(0,0), (1,0), (2,0)],
    [(0,0), (0,1), (0,2)],
    [(0,0), (1,0), (2,0), (3,0)],
    [(0,0), (0,1), (0,2), (0,3)],
    [(0,0), (1,0), (0,1), (1,1)],
    [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1), (0,2), (1,2), (2,2)],
    [(0,0), (0,1), (1,1)],
    [(0,0), (0,1), (0,2), (1,2)],
    [(0,0), (1,0), (2,0), (1,1)]
]

NIVELES_PUZLE = [
    {
        "nombre": "Nivel 1: Limpieza Básica",
        "tablero": [
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [1,1,1,1,0,1,1,1],
            [1,1,1,1,0,1,1,1],
            [1,1,1,1,0,1,1,1],
            [1,1,1,1,0,1,1,1]
        ]
    },
    {
        "nombre": "Nivel 2: La Cruz",
        "tablero": [
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [1,1,1,0,0,1,1,1],
            [1,1,1,0,0,1,1,1],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0]
        ]
    },
    {
        "nombre": "Nivel 3: El Tablero de Ajedrez",
        "tablero": [
            [1,0,1,0,1,0,1,0],
            [0,1,0,1,0,1,0,1],
            [1,0,1,0,1,0,1,0],
            [0,1,0,1,0,1,0,1],
            [1,0,1,0,1,0,1,0],
            [0,1,0,1,0,1,0,1],
            [1,0,1,0,1,0,1,0],
            [0,1,0,1,0,1,0,1]
        ]
    }
]

LOGROS_DEFINICION = [
    {"id": "limpieza_total", "titulo": "✨ Limpieza Total", "desc": "Limpia completamente el tablero.", "icono": "🧹"},
    {"id": "combo_imparable", "titulo": "🔥 Combo Imparable", "desc": "Consigue un combo x4 o superior.", "icono": "🔥"},
    {"id": "bombardero", "titulo": "💣 Bombardero Expert", "desc": "Detona 5 o más bombas en partida.", "icono": "💣"},
    {"id": "puzle_maestro", "titulo": "🧩 Maestro Puzle", "desc": "Completa con éxito un nivel puzle.", "icono": "🧩"}
]

ARCHIVO_RECORDS = "highscores.json"
ARCHIVO_GUARDADO = "partida_guardada.json"
ARCHIVO_LOGROS = "logros.json"

# --- GESTOR DE AUDIO SINTÉTICO ---
class GestorSonidos:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.activo = True
            self.canal_musica = pygame.mixer.Channel(0)
            self.canal_efectos = pygame.mixer.Channel(1)
            self.musica_snd = self._generar_musica_chiptune()
        except:
            self.activo = False

    def _generar_tono(self, freq_inicio, freq_fin, duracion, tipo="sine", volumen=1.0):
        if not self.activo: return None
        n_samples = int(22050 * duracion)
        buf = array.array('h')
        for i in range(n_samples):
            t = float(i) / n_samples
            freq = freq_inicio + (freq_fin - freq_inicio) * t
            if tipo == "sine":
                v = math.sin(2.0 * math.pi * freq * (i / 22050.0))
            elif tipo == "square":
                v = 0.4 if math.sin(2.0 * math.pi * freq * (i / 22050.0)) > 0 else -0.4
            elif tipo == "noise":
                v = random.uniform(-0.8, 0.8)
            env = 1.0 - t
            val = int(v * env * 12000 * volumen)
            val = max(-32768, min(32767, val))
            buf.append(val)
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)

    def _generar_musica_chiptune(self):
        if not self.activo: return None
        duracion_nota = 0.15
        notas = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        patron = [0, 2, 4, 7, 4, 2, 0, -1, 1, 3, 5, 7, 5, 3, 1, -1]
        buf = array.array('h')
        
        for idx in patron:
            n_samples = int(22050 * duracion_nota)
            freq = notas[idx] if idx != -1 else 0
            for i in range(n_samples):
                if freq > 0:
                    v = 0.15 if math.sin(2.0 * math.pi * freq * (i / 22050.0)) > 0 else -0.15
                else:
                    v = 0.0
                val = int(v * 8000)
                buf.append(val)
                buf.append(val)
        return pygame.mixer.Sound(buffer=buf)

    def reproducir_musica(self):
        if not self.activo or not self.musica_snd: return
        if not self.canal_musica.get_busy():
            self.canal_musica.play(self.musica_snd, loops=-1)

    def detener_musica(self):
        if self.activo:
            self.canal_musica.stop()

    def play_colocar(self):
        snd = self._generar_tono(150, 80, 0.08, "square")
        if snd: self.canal_efectos.play(snd)

    def play_limpiar(self, combo=1):
        freq_base = 300 + (combo * 80)
        snd = self._generar_tono(freq_base, freq_base + 300, 0.2, "sine")
        if snd: self.canal_efectos.play(snd)

    def play_bomba(self):
        snd = self._generar_tono(120, 30, 0.35, "noise")
        if snd: self.canal_efectos.play(snd)

    def play_rotar(self):
        snd = self._generar_tono(350, 500, 0.05, "sine")
        if snd: self.canal_efectos.play(snd)

    def play_undo(self):
        snd = self._generar_tono(500, 250, 0.1, "sine")
        if snd: self.canal_efectos.play(snd)

    def play_logro(self):
        snd = self._generar_tono(523.25, 1046.50, 0.3, "sine")
        if snd: self.canal_efectos.play(snd)

# --- PARTÍCULAS, DESTELLOS Y TEXTOS ---
class Particula:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-6, 2)
        self.radio = random.uniform(3, 8)
        self.vida = 255

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.22
        self.vida -= 8
        if self.radio > 0.5:
            self.radio -= 0.15

    def dibujar(self, pantalla):
        if self.vida > 0:
            surf = pygame.Surface((int(self.radio * 2), int(self.radio * 2)), pygame.SRCALPHA)
            color_alpha = (*self.color, max(0, int(self.vida)))
            pygame.draw.circle(surf, color_alpha, (int(self.radio), int(self.radio)), int(self.radio))
            pantalla.blit(surf, (self.x - self.radio, self.y - self.radio))

class DestelloLinea:
    def __init__(self, es_fila, indice):
        self.es_fila = es_fila
        self.indice = indice
        self.vida = 255
        
        if es_fila:
            self.rect = pygame.Rect(
                POS_TABLERO_X, 
                POS_TABLERO_Y + indice * (TAMANO_CELDA + MARGEN), 
                ANCHO_TABLERO, 
                TAMANO_CELDA
            )
        else:
            self.rect = pygame.Rect(
                POS_TABLERO_X + indice * (TAMANO_CELDA + MARGEN), 
                POS_TABLERO_Y, 
                TAMANO_CELDA, 
                ANCHO_TABLERO
            )

    def actualizar(self):
        self.vida -= 20

    def dibujar(self, pantalla):
        if self.vida > 0:
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            alpha = max(0, int(self.vida))
            s.fill((255, 255, 255, min(255, alpha)))
            pygame.draw.rect(s, (*COLOR_DORADO, alpha), s.get_rect(), width=4, border_radius=6)
            pantalla.blit(s, self.rect.topleft)

class TextoFlotante:
    def __init__(self, x, y, texto, color, escala_extra=1.0):
        self.x = x
        self.y = y
        self.texto = texto
        self.color = color
        self.vida = 255
        self.vy = -2.0
        self.escala_extra = escala_extra

    def actualizar(self):
        self.y += self.vy
        self.vida -= 4

    def dibujar(self, pantalla, fuente):
        if self.vida > 0:
            surf = fuente.render(self.texto, True, self.color)
            if self.escala_extra > 1.0:
                w, h = surf.get_size()
                surf = pygame.transform.smoothscale(surf, (int(w * self.escala_extra), int(h * self.escala_extra)))
            surf.set_alpha(max(0, int(self.vida)))
            pantalla.blit(surf, (self.x - surf.get_width() // 2, self.y))

class NotificacionLogro:
    def __init__(self, titulo):
        self.titulo = titulo
        self.vida = 180
        self.y_target = 20
        self.y_curr = -60

    def actualizar(self):
        self.vida -= 1
        if self.vida > 150:
            self.y_curr += (self.y_target - self.y_curr) * 0.2
        elif self.vida < 30:
            self.y_curr += (-70 - self.y_curr) * 0.2

    def dibujar(self, pantalla, fuente):
        rect = pygame.Rect(ANCHO_VIRTUAL // 2 - 140, int(self.y_curr), 280, 45)
        pygame.draw.rect(pantalla, (20, 30, 45), rect, border_radius=10)
        pygame.draw.rect(pantalla, COLOR_DORADO, rect, width=2, border_radius=10)
        
        txt_sub = fuente.render("🏆 ¡LOGRO DESBLOQUEADO!", True, COLOR_DORADO)
        txt_tit = fuente.render(self.titulo, True, COLOR_TEXTO)
        pantalla.blit(txt_sub, (rect.centerx - txt_sub.get_width() // 2, rect.y + 5))
        pantalla.blit(txt_tit, (rect.centerx - txt_tit.get_width() // 2, rect.y + 22))

# --- CLASE PIEZA ---
class Pieza:
    def __init__(self, forma, color, slot_index, tipo="normal", multiplicador=1):
        self.forma = list(forma)
        self.color = color
        self.slot_index = slot_index
        self.tipo = tipo  # "normal", "bomba", "arcoiris"
        self.multiplicador = multiplicador
        
        self.pos_origen_x = POS_TABLERO_X + 20 + slot_index * 125 if slot_index >= 0 else 0
        self.pos_origen_y = 660
        self.x = self.pos_origen_x
        self.y = self.pos_origen_y
        
        self.arrastrando = False
        self.escala_preview = 0.5
        self.normalizar_forma()

    def normalizar_forma(self):
        if not self.forma: return
        min_x = min(bx for bx, by in self.forma)
        min_y = min(by for bx, by in self.forma)
        self.forma = [(bx - min_x, by - min_y) for bx, by in self.forma]

    def rotar(self):
        if self.tipo != "normal":
            return
        self.forma = [(by, -bx) for bx, by in self.forma]
        self.normalizar_forma()

    def obtener_ancho_alto(self, escala=1.0):
        max_x = max(b[0] for b in self.forma) + 1
        max_y = max(b[1] for b in self.forma) + 1
        tam = TAMANO_CELDA * escala
        ancho = max_x * tam + (max_x - 1) * (MARGEN * escala)
        alto = max_y * tam + (max_y - 1) * (MARGEN * escala)
        return ancho, alto

    def obtener_rects(self, pos_x=None, pos_y=None, escala=1.0, inflar=0):
        if pos_x is None: pos_x = self.x
        if pos_y is None: pos_y = self.y
        rects = []
        tam = TAMANO_CELDA * escala
        m_scaled = MARGEN * escala
        for bx, by in self.forma:
            rx = pos_x + bx * (tam + m_scaled)
            ry = pos_y + by * (tam + m_scaled)
            r = pygame.Rect(rx, ry, tam, tam)
            if inflar > 0:
                r = r.inflate(inflar, inflar)
            rects.append(r)
        return rects

    def dibujar(self, pantalla, fuente, t_anim=0):
        escala = 1.0 if self.arrastrando else self.escala_preview
        offset_float = 0
        if not self.arrastrando and self.slot_index >= 0:
            offset_float = math.sin(t_anim * 0.004 + self.slot_index) * 4

        rects = self.obtener_rects(pos_y=self.y + offset_float, escala=escala)

        if self.arrastrando:
            for rect in self.obtener_rects(pos_x=self.x + 8, pos_y=self.y + 8, escala=escala):
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                s.fill((0, 0, 0, 80))
                pantalla.blit(s, rect.topleft)

        for rect in rects:
            if self.tipo == "arcoiris":
                r = int((math.sin(t_anim * 0.005) + 1) * 127)
                g = int((math.sin(t_anim * 0.005 + 2) + 1) * 127)
                b = int((math.sin(t_anim * 0.005 + 4) + 1) * 127)
                col = (r, g, b)
            else:
                col = self.color

            surf_glow = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(surf_glow, (*col, 35), surf_glow.get_rect(), border_radius=8)
            pantalla.blit(surf_glow, (rect.x - 4, rect.y - 4))

            pygame.draw.rect(pantalla, col, rect, border_radius=6)
            brillo = tuple(min(255, c + 70) for c in col)
            pygame.draw.line(pantalla, brillo, (rect.left + 2, rect.top + 2), (rect.right - 2, rect.top + 2), width=2)
            pygame.draw.line(pantalla, brillo, (rect.left + 2, rect.top + 2), (rect.left + 2, rect.bottom - 2), width=2)

            if self.tipo == "bomba":
                pygame.draw.circle(pantalla, (10, 10, 10), rect.center, int(rect.width * 0.25))
                pygame.draw.circle(pantalla, (255, 60, 0), rect.center, int(rect.width * 0.12))

            if self.multiplicador > 1:
                pygame.draw.rect(pantalla, COLOR_DORADO, rect, width=2, border_radius=6)
                txt = fuente.render(f"x{self.multiplicador}", True, COLOR_DORADO)
                pantalla.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def reset_pos(self):
        self.x = self.pos_origen_x
        self.y = self.pos_origen_y
        self.arrastrando = False

    def to_dict(self):
        return {
            "forma": self.forma,
            "color": list(self.color),
            "slot_index": self.slot_index,
            "tipo": self.tipo,
            "multiplicador": self.multiplicador
        }

    @staticmethod
    def from_dict(data):
        return Pieza(
            data["forma"],
            tuple(data["color"]),
            data["slot_index"],
            data["tipo"],
            data.get("multiplicador", 1)
        )

# --- CLASE PRINCIPAL DEL JUEGO CON ESCALADO DINÁMICO DE PANTALLA ---
class JuegoBlockBlast:
    def __init__(self):
        pygame.init()
        
        # Obtener resolución real de la pantalla del móvil o ventana
        info = pygame.display.Info()
        self.ancho_real = info.current_w if info.current_w > 0 else ANCHO_VIRTUAL
        self.alto_real = info.current_h if info.current_h > 0 else ALTO_VIRTUAL

        # Configurar pantalla completa en móviles o ventana adaptable
        self.pantalla_real = pygame.display.set_mode((self.ancho_real, self.alto_real), pygame.RESIZABLE | pygame.FULLSCREEN)
        pygame.display.set_caption("BLOCK DESTROYER DELUXE")
        
        # Superficie de renderizado Virtual (Todas las operaciones internas se dibujan aquí)
        self.pantalla = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))

        self.reloj = pygame.time.Clock()
        self.fuente_micro = pygame.font.SysFont("arial", 12, bold=True)
        self.fuente_peque = pygame.font.SysFont("arial", 15)
        self.fuente = pygame.font.SysFont("arial", 20, bold=True)
        self.fuente_grande = pygame.font.SysFont("arial", 32, bold=True)
        self.fuente_titulo = pygame.font.SysFont("arial", 38, bold=True)
        self.fuente_titulo_gigante = pygame.font.SysFont("arial", 42, bold=True)
        self.sonidos = GestorSonidos()

        # Detección para toques táctiles (Móvil)
        self.tiempo_inicio_toque = 0
        self.pos_inicio_toque = (0, 0)

        self.tablero = [[None for _ in range(8)] for _ in range(8)]
        self.puntuacion = 0
        self.combo = 0
        self.modo_juego = "clasico"
        self.nivel_puzle_actual = 0
        self.tiempo_restante = 60.0

        self.high_scores = self.cargar_puntuaciones()
        self.logros_desbloqueados = self.cargar_logros()

        self.piezas_disponibles = []
        self.pieza_reserva = None
        self.pieza_seleccionada = None
        self.origen_seleccion = None
        
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.particulas = []
        self.destellos = []
        self.textos_flotantes = []
        self.notificaciones = []

        self.historial_estados = []
        self.undo_restantes = 3
        self.bombas_detonadas = 0

        self.shake_time = 0
        self.shake_magnitude = 0

        self.game_over = False
        self.victoria_puzle = False
        self.pidiendo_nombre = False
        self.nombre_jugador = ""
        self.mostrando_records = False
        self.mostrando_ayuda = False
        self.mostrando_logros = False
        self.mostrando_menu_pausa = False
        self.seleccionar_modo = True
        self.seleccionar_puzle = False

        # BOTONES HUD Y MENÚS (Basados en dimensiones virtuales)
        self.btn_logros_hud = pygame.Rect(ANCHO_VIRTUAL - 110, 10, 95, 26)
        self.btn_top10 = pygame.Rect(ANCHO_VIRTUAL - 110, 40, 95, 26)
        self.btn_ayuda = pygame.Rect(ANCHO_VIRTUAL - 110, 70, 95, 26)
        self.btn_menu_hud = pygame.Rect(ANCHO_VIRTUAL - 110, 100, 95, 26)
        
        self.btn_undo = pygame.Rect(POS_TABLERO_X - 55, POS_TABLERO_Y + 180, 45, 45)
        self.zone_hold = pygame.Rect(POS_TABLERO_X - 60, POS_TABLERO_Y + 10, 52, 100)
        self.zone_bandeja = pygame.Rect(POS_TABLERO_X - 10, 640, ANCHO_TABLERO + 20, 150)

        # POSICIÓN DE BOTONES DEL MENÚ
        self.btn_continuar = pygame.Rect(ANCHO_VIRTUAL // 2 - 150, 220, 300, 48)
        self.btn_modo_clasico = pygame.Rect(ANCHO_VIRTUAL // 2 - 150, 280, 300, 48)
        self.btn_modo_tiempo = pygame.Rect(ANCHO_VIRTUAL // 2 - 150, 340, 300, 48)
        self.btn_modo_puzle = pygame.Rect(ANCHO_VIRTUAL // 2 - 150, 400, 300, 48)
        self.btn_logros_menu = pygame.Rect(ANCHO_VIRTUAL // 2 - 150, 460, 300, 45)
        self.btn_ayuda_menu = pygame.Rect(ANCHO_VIRTUAL // 2 - 150, 515, 300, 45)

        self.btn_pausa_continuar = pygame.Rect(ANCHO_VIRTUAL // 2 - 140, 270, 280, 50)
        self.btn_pausa_guardar = pygame.Rect(ANCHO_VIRTUAL // 2 - 140, 340, 280, 50)
        self.btn_pausa_finalizar = pygame.Rect(ANCHO_VIRTUAL // 2 - 140, 410, 280, 50)

        # OBJETOS DECORATIVOS PARA MENÚ PRINCIPAL
        self.piezas_fondo_menu = []
        for _ in range(16):
            self.piezas_fondo_menu.append({
                "x": random.randint(10, ANCHO_VIRTUAL - 70),
                "y": random.randint(-200, ALTO_VIRTUAL),
                "vy": random.uniform(1.2, 3.2),
                "forma": random.choice(FORMAS),
                "color": random.choice(COLORES_PIEZAS),
                "escala": random.uniform(0.5, 0.8)
            })

    # --- MAPEO DE COORDENADAS PANTALLA REAL -> PANTALLA VIRTUAL ---
    def obtener_pos_virtual(self, pos_real):
        escala_x = self.ancho_real / ANCHO_VIRTUAL
        escala_y = self.alto_real / ALTO_VIRTUAL
        escala = min(escala_x, escala_y)

        ancho_dibujado = ANCHO_VIRTUAL * escala
        alto_dibujado = ALTO_VIRTUAL * escala

        offset_x = (self.ancho_real - ancho_dibujado) / 2
        offset_y = (self.alto_real - alto_dibujado) / 2

        vx = (pos_real[0] - offset_x) / escala
        vy = (pos_real[1] - offset_y) / escala
        return vx, vy

    # --- DIBUJAR PANTALLA ESCALADA AUTOMÁTICAMENTE ---
    def renderizar_pantalla_escalada(self):
        escala_x = self.ancho_real / ANCHO_VIRTUAL
        escala_y = self.alto_real / ALTO_VIRTUAL
        escala = min(escala_x, escala_y)

        ancho_dibujado = int(ANCHO_VIRTUAL * escala)
        alto_dibujado = int(ALTO_VIRTUAL * escala)

        offset_x = (self.ancho_real - ancho_dibujado) // 2
        offset_y = (self.alto_real - alto_dibujado) // 2

        self.pantalla_real.fill((0, 0, 0)) # Fondo de barras negras para letterboxing
        superficie_escalada = pygame.transform.smoothscale(self.pantalla, (ancho_dibujado, alto_dibujado))
        self.pantalla_real.blit(superficie_escalada, (offset_x, offset_y))
        pygame.display.flip()

    # --- PERSISTENCIA Y REGISTROS ---
    def cargar_puntuaciones(self):
        if os.path.exists(ARCHIVO_RECORDS):
            try:
                with open(ARCHIVO_RECORDS, "r") as f: return json.load(f)
            except: pass
        return []

    def guardar_puntuaciones(self):
        try:
            with open(ARCHIVO_RECORDS, "w") as f: json.dump(self.high_scores, f)
        except: pass

    def cargar_logros(self):
        if os.path.exists(ARCHIVO_LOGROS):
            try:
                with open(ARCHIVO_LOGROS, "r") as f: return set(json.load(f))
            except: pass
        return set()

    def guardar_logros(self):
        try:
            with open(ARCHIVO_LOGROS, "w") as f: json.dump(list(self.logros_desbloqueados), f)
        except: pass

    def hay_partida_guardada(self):
        return os.path.exists(ARCHIVO_GUARDADO)

    def guardar_partida(self):
        data = {
            "tablero": [[list(c) if isinstance(c, tuple) else c for c in fila] for fila in self.tablero],
            "puntuacion": self.puntuacion,
            "combo": self.combo,
            "modo_juego": self.modo_juego,
            "tiempo_restante": self.tiempo_restante,
            "piezas": [p.to_dict() for p in self.piezas_disponibles],
            "pieza_reserva": self.pieza_reserva.to_dict() if self.pieza_reserva else None,
            "undo_restantes": self.undo_restantes,
            "nivel_puzle": self.nivel_puzle_actual
        }
        try:
            with open(ARCHIVO_GUARDADO, "w") as f: json.dump(data, f)
        except Exception as e: print(f"Error guardando: {e}")

    def cargar_partida(self):
        if not self.hay_partida_guardada(): return False
        try:
            with open(ARCHIVO_GUARDADO, "r") as f: data = json.load(f)
            self.tablero = [[tuple(c) if isinstance(c, list) else c for c in fila] for fila in data["tablero"]]
            self.puntuacion = data["puntuacion"]
            self.combo = data["combo"]
            self.modo_juego = data["modo_juego"]
            self.tiempo_restante = data["tiempo_restante"]
            self.piezas_disponibles = [Pieza.from_dict(p) for p in data["piezas"]]
            self.pieza_reserva = Pieza.from_dict(data["pieza_reserva"]) if data["pieza_reserva"] else None
            self.undo_restantes = data.get("undo_restantes", 3)
            self.nivel_puzle_actual = data.get("nivel_puzle", 0)
            
            self.seleccionar_modo = False
            self.game_over = False
            self.mostrando_menu_pausa = False
            self.sonidos.reproducir_musica()
            return True
        except Exception as e:
            print(f"Error al cargar: {e}")
            return False

    def borrar_partida_guardada(self):
        if os.path.exists(ARCHIVO_GUARDADO):
            try: os.remove(ARCHIVO_GUARDADO)
            except: pass

    # --- HISTORIAL Y DESHACER ---
    def guardar_estado_historial(self):
        estado = {
            "tablero": copy.deepcopy(self.tablero),
            "puntuacion": self.puntuacion,
            "combo": self.combo,
            "piezas": [p.to_dict() for p in self.piezas_disponibles],
            "pieza_reserva": self.pieza_reserva.to_dict() if self.pieza_reserva else None,
            "tiempo_restante": self.tiempo_restante
        }
        self.historial_estados.append(estado)
        if len(self.historial_estados) > 5:
            self.historial_estados.pop(0)

    def ejecutar_deshacer(self):
        if self.undo_restantes > 0 and self.historial_estados:
            estado = self.historial_estados.pop()
            self.tablero = estado["tablero"]
            self.puntuacion = estado["puntuacion"]
            self.combo = estado["combo"]
            self.piezas_disponibles = [Pieza.from_dict(p) for p in estado["piezas"]]
            self.pieza_reserva = Pieza.from_dict(estado["pieza_reserva"]) if estado["pieza_reserva"] else None
            self.tiempo_restante = estado["tiempo_restante"]
            self.undo_restantes -= 1
            self.sonidos.play_undo()
            self.textos_flotantes.append(TextoFlotante(self.btn_undo.centerx, self.btn_undo.y - 10, "¡DESHECHO!", COLOR_DORADO))

    # --- LÓGICA DE HOLD Y BANDEJA ---
    def guardar_en_hold(self, pieza):
        if self.pieza_reserva is None:
            self.guardar_estado_historial()
            self.pieza_reserva = pieza
            if pieza in self.piezas_disponibles:
                self.piezas_disponibles.remove(pieza)
            self.pieza_reserva.slot_index = -1
            self.pieza_reserva.reset_pos()
            self.sonidos.play_rotar()
            
            if not self.piezas_disponibles:
                self.generar_piezas()

    def generar_piezas(self):
        self.piezas_disponibles = []
        for i in range(3):
            prob = random.random()
            if prob < 0.03:
                pieza = Pieza([(0,0)], (80, 80, 80), i, tipo="bomba")
            elif prob < 0.07:
                pieza = Pieza([(0,0)], (255, 255, 255), i, tipo="arcoiris")
            else:
                mult_rand = random.random()
                if mult_rand < 0.03: mult = 3
                elif mult_rand < 0.10: mult = 2
                else: mult = 1
                
                forma = random.choice(FORMAS)
                color = random.choice(COLORES_PIEZAS)
                pieza = Pieza(forma, color, i, tipo="normal", multiplicador=mult)
                
            self.piezas_disponibles.append(pieza)

    def iniciar_nivel_puzle(self, index_nivel):
        self.modo_juego = "puzle"
        self.nivel_puzle_actual = index_nivel
        cfg = NIVELES_PUZLE[index_nivel]
        self.tablero = [[COLOR_BOTON if cell == 1 else None for cell in fila] for fila in cfg["tablero"]]
        self.puntuacion = 0
        self.combo = 0
        self.generar_piezas()
        self.seleccionar_puzle = False
        self.seleccionar_modo = False
        self.sonidos.reproducir_musica()

    def x_y_a_grid(self, px, py):
        rel_x = px - POS_TABLERO_X
        rel_y = py - POS_TABLERO_Y
        paso = TAMANO_CELDA + MARGEN
        
        col = round(rel_x / paso)
        fila = round(rel_y / paso)

        if -0.45 <= (rel_x / paso) < 8.45 and -0.45 <= (rel_y / paso) < 8.45:
            col = max(0, min(7, col))
            fila = max(0, min(7, fila))
            return col, fila
            
        return None, None

    def puede_colocar(self, pieza, col_inicio, fila_inicio):
        for bx, by in pieza.forma:
            c = col_inicio + bx
            f = fila_inicio + by
            if c < 0 or c >= 8 or f < 0 or f >= 8: return False
            if self.tablero[f][c] is not None: return False
        return True

    def colocar_pieza(self, pieza, col_inicio, fila_inicio):
        self.guardar_estado_historial()

        if pieza.tipo == "bomba":
            self.sonidos.play_bomba()
            self.activar_screen_shake(12, 0.25)
            self.bombas_detonadas += 1
            if self.bombas_detonadas >= 5:
                self.desbloquear_logro("bombardero", "💣 Bombardero Expert")
                
            for f in range(max(0, fila_inicio - 1), min(8, fila_inicio + 2)):
                for c in range(max(0, col_inicio - 1), min(8, col_inicio + 2)):
                    if self.tablero[f][c]:
                        col_p = self.tablero[f][c] if isinstance(self.tablero[f][c], tuple) else COLOR_DORADO
                        self.generar_particulas_casilla(c, f, col_p)
                        self.tablero[f][c] = None
            self.puntuacion += 150
            self.textos_flotantes.append(TextoFlotante(pieza.x + 20, pieza.y, "¡BOOM! +150", (255, 100, 0)))

        elif pieza.tipo == "arcoiris":
            self.sonidos.play_limpiar()
            self.activar_screen_shake(8, 0.2)
            self.destellos.append(DestelloLinea(True, fila_inicio))
            self.destellos.append(DestelloLinea(False, col_inicio))
            
            for f in range(8):
                if self.tablero[f][col_inicio]:
                    col_p = self.tablero[f][col_inicio] if isinstance(self.tablero[f][col_inicio], tuple) else COLOR_DORADO
                    self.generar_particulas_casilla(col_inicio, f, col_p)
                    self.tablero[f][col_inicio] = None
            for c in range(8):
                if self.tablero[fila_inicio][c]:
                    col_p = self.tablero[fila_inicio][c] if isinstance(self.tablero[fila_inicio][c], tuple) else COLOR_DORADO
                    self.generar_particulas_casilla(c, fila_inicio, col_p)
                    self.tablero[fila_inicio][c] = None
            self.puntuacion += 300
            self.textos_flotantes.append(TextoFlotante(pieza.x + 20, pieza.y, "¡ARCOÍRIS! +300", COLOR_DORADO))
            if self.modo_juego == "tiempo": self.tiempo_restante += 5.0

        else:
            self.sonidos.play_colocar()
            for bx, by in pieza.forma:
                c = col_inicio + bx
                f = fila_inicio + by
                self.tablero[f][c] = (pieza.color, pieza.multiplicador)
            
            puntos_colocacion = len(pieza.forma) * 10 * pieza.multiplicador
            self.puntuacion += puntos_colocacion
            self.verificar_lineas()

        if self.origen_seleccion == "hold":
            self.pieza_reserva = None
        elif pieza in self.piezas_disponibles:
            self.piezas_disponibles.remove(pieza)

        if not self.piezas_disponibles and self.pieza_reserva is None:
            self.generar_piezas()
        elif not self.piezas_disponibles and self.pieza_reserva is not None:
            self.generar_piezas()

        if all(cell is None for fila in self.tablero for cell in fila):
            self.desbloquear_logro("limpieza_total", "✨ Limpieza Total")
            self.activar_screen_shake(18, 0.45)
            self.puntuacion += 1000
            self.sonidos.play_logro()
            
            for _ in range(35):
                rx = random.randint(POS_TABLERO_X, POS_TABLERO_X + ANCHO_TABLERO)
                ry = random.randint(POS_TABLERO_Y, POS_TABLERO_Y + ANCHO_TABLERO)
                self.particulas.append(Particula(rx, ry, COLOR_DORADO))

            self.textos_flotantes.append(
                TextoFlotante(ANCHO_VIRTUAL // 2, POS_TABLERO_Y + 150, "¡TABLERO VACÍO! +1000", COLOR_DORADO, 1.5)
            )

        if self.modo_juego == "puzle":
            if all(cell is None for fila in self.tablero for cell in fila):
                self.victoria_puzle = True
                self.desbloquear_logro("puzle_maestro", "🧩 Maestro Puzle")
                self.evaluar_record()

        self.verificar_game_over()

    def activar_screen_shake(self, magnitud, duracion):
        self.shake_magnitude = magnitud
        self.shake_time = duracion

    def generar_particulas_casilla(self, col, fila, color_data):
        color = color_data[0] if isinstance(color_data, tuple) and isinstance(color_data[0], tuple) else (color_data if isinstance(color_data, tuple) else COLOR_DORADO)
        x_base = POS_TABLERO_X + col * (TAMANO_CELDA + MARGEN) + TAMANO_CELDA // 2
        y_base = POS_TABLERO_Y + fila * (TAMANO_CELDA + MARGEN) + TAMANO_CELDA // 2
        for _ in range(8):
            self.particulas.append(Particula(x_base, y_base, color))

    def verificar_lineas(self):
        filas_a_limpiar = [f for f in range(8) if all(self.tablero[f][c] is not None for c in range(8))]
        cols_a_limpiar = [c for c in range(8) if all(self.tablero[f][c] is not None for f in range(8))]

        mult_acumulado = 1

        for f in filas_a_limpiar:
            self.destellos.append(DestelloLinea(True, f))
            for c in range(8):
                cell = self.tablero[f][c]
                if cell:
                    if isinstance(cell, tuple) and len(cell) == 2:
                        mult_acumulado = max(mult_acumulado, cell[1])
                    self.generar_particulas_casilla(c, f, cell)
                    self.tablero[f][c] = None

        for c in cols_a_limpiar:
            self.destellos.append(DestelloLinea(False, c))
            for f in range(8):
                cell = self.tablero[f][c]
                if cell:
                    if isinstance(cell, tuple) and len(cell) == 2:
                        mult_acumulado = max(mult_acumulado, cell[1])
                    self.generar_particulas_casilla(c, f, cell)
                    self.tablero[f][c] = None

        total_lineas = len(filas_a_limpiar) + len(cols_a_limpiar)
        if total_lineas > 0:
            self.combo += 1
            if self.combo >= 4:
                self.desbloquear_logro("combo_imparable", "🔥 Combo Imparable")

            self.sonidos.play_limpiar(self.combo)
            self.activar_screen_shake(6 + total_lineas * 2, 0.2)

            puntos_base = (total_lineas * 100 * total_lineas) * self.combo * mult_acumulado
            self.puntuacion += puntos_base
            
            if self.modo_juego == "tiempo":
                self.tiempo_restante += total_lineas * 3.0

            txt_comb = f"¡+{puntos_base}!"
            if self.combo > 1 or mult_acumulado > 1:
                txt_comb = f"¡COMBO x{self.combo}! +{puntos_base}"
                if mult_acumulado > 1: txt_comb += f" (Mult x{mult_acumulado})"
            
            self.textos_flotantes.append(TextoFlotante(ANCHO_VIRTUAL // 2, POS_TABLERO_Y - 20, txt_comb, COLOR_DORADO, 1.2 if self.combo > 2 else 1.0))
        else:
            self.combo = 0

    def verificar_game_over(self):
        piezas_comprobar = self.piezas_disponibles + ([self.pieza_reserva] if self.pieza_reserva else [])
        for pieza in piezas_comprobar:
            if pieza.tipo in ["bomba", "arcoiris"]:
                return
            for f in range(8):
                for c in range(8):
                    if self.puede_colocar(pieza, c, f):
                        return
        self.game_over = True
        self.borrar_partida_guardada()
        self.evaluar_record()

    def desbloquear_logro(self, logro_id, titulo):
        if logro_id not in self.logros_desbloqueados:
            self.logros_desbloqueados.add(logro_id)
            self.guardar_logros()
            self.notificaciones.append(NotificacionLogro(titulo))
            self.sonidos.play_logro()

    def finalizar_partida_manual(self):
        self.mostrando_menu_pausa = False
        self.borrar_partida_guardada()
        self.evaluar_record()

    def evaluar_record(self):
        self.sonidos.detener_musica()
        es_top_10 = False
        if len(self.high_scores) < 10 or self.puntuacion > self.high_scores[-1]["score"]:
            es_top_10 = True
        if es_top_10 and self.puntuacion > 0:
            self.pidiendo_nombre = True
            self.nombre_jugador = ""
        else:
            self.mostrando_records = True

    def guardar_record_actual(self):
        nombre = self.nombre_jugador.strip().upper()
        if not nombre: nombre = "AAAA"
        elif len(nombre) < 4: nombre = nombre.ljust(4, "_")
            
        self.high_scores.append({"name": nombre, "score": self.puntuacion})
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:10]
        self.guardar_puntuaciones()
        self.pidiendo_nombre = False
        self.mostrando_records = True

    # --- COMPONENTES DE INTERFAZ Y RENDER ---
    def dibujar_boton_decorado(self, rect, texto, color_base, color_borde, pos_mous):
        hover = rect.collidepoint(pos_mous)
        col_f = tuple(min(255, c + 25) for c in color_base) if hover else color_base
        
        rect_sombra = rect.copy()
        rect_sombra.y += 4
        pygame.draw.rect(self.pantalla, (10, 12, 18), rect_sombra, border_radius=12)
        
        pygame.draw.rect(self.pantalla, col_f, rect, border_radius=12)
        pygame.draw.rect(self.pantalla, color_borde, rect, width=3, border_radius=12)
        
        rect_brillo = pygame.Rect(rect.x + 5, rect.y + 4, rect.width - 10, rect.height // 3)
        s_brillo = pygame.Surface((rect_brillo.width, rect_brillo.height), pygame.SRCALPHA)
        s_brillo.fill((255, 255, 255, 30))
        self.pantalla.blit(s_brillo, rect_brillo.topleft)

        txt = self.fuente.render(texto, True, COLOR_TEXTO)
        txt_sombra = self.fuente.render(texto, True, (0, 0, 0))
        self.pantalla.blit(txt_sombra, (rect.centerx - txt.get_width() // 2 + 1, rect.centery - txt.get_height() // 2 + 1))
        self.pantalla.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def ejecutar(self):
        while True:
            dt = self.reloj.tick(60) / 1000.0
            t_anim = pygame.time.get_ticks()

            # Mapear posición real del ratón/toque a posición virtual
            pos_mous_real = pygame.mouse.get_pos()
            pos_mous = self.obtener_pos_virtual(pos_mous_real)

            shake_offset_x, shake_offset_y = 0, 0
            if self.shake_time > 0:
                self.shake_time -= dt
                shake_offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
                shake_offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)

            if not self.seleccionar_modo and not self.game_over and not self.mostrando_records and not self.mostrando_ayuda and not self.mostrando_logros and not self.mostrando_menu_pausa and self.modo_juego == "tiempo":
                self.tiempo_restante -= dt
                if self.tiempo_restante <= 0:
                    self.tiempo_restante = 0
                    self.game_over = True
                    self.borrar_partida_guardada()
                    self.evaluar_record()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Adaptar tamaño de pantalla si el móvil rota o cambia resolución
                elif evento.type == pygame.VIDEORESIZE:
                    self.ancho_real, self.alto_real = evento.w, evento.h
                    self.pantalla_real = pygame.display.set_mode((self.ancho_real, self.alto_real), pygame.RESIZABLE | pygame.FULLSCREEN)

                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    if not self.seleccionar_modo and not self.seleccionar_puzle and not self.game_over and not self.pidiendo_nombre:
                        self.mostrando_menu_pausa = not self.mostrando_menu_pausa
                        if self.pieza_seleccionada:
                            self.pieza_seleccionada.reset_pos()
                            self.pieza_seleccionada = None

                if self.mostrando_menu_pausa:
                    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        if self.btn_pausa_continuar.collidepoint(pos_mous):
                            self.mostrando_menu_pausa = False
                        elif self.btn_pausa_guardar.collidepoint(pos_mous):
                            self.guardar_partida()
                            self.sonidos.detener_musica()
                            self.__init__()
                        elif self.btn_pausa_finalizar.collidepoint(pos_mous):
                            self.finalizar_partida_manual()
                    continue

                if self.mostrando_ayuda or self.mostrando_logros:
                    if evento.type == pygame.MOUSEBUTTONDOWN:
                        self.mostrando_ayuda = False
                        self.mostrando_logros = False
                    continue

                if self.seleccionar_puzle:
                    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        for idx in range(len(NIVELES_PUZLE)):
                            r_btn = pygame.Rect(ANCHO_VIRTUAL // 2 - 140, 220 + idx * 70, 280, 55)
                            if r_btn.collidepoint(pos_mous):
                                self.iniciar_nivel_puzle(idx)
                                break
                    continue

                if self.seleccionar_modo:
                    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        if self.hay_partida_guardada() and self.btn_continuar.collidepoint(pos_mous):
                            self.cargar_partida()
                        elif self.btn_modo_clasico.collidepoint(pos_mous):
                            self.modo_juego = "clasico"
                            self.seleccionar_modo = False
                            self.generar_piezas()
                            self.sonidos.reproducir_musica()
                        elif self.btn_modo_tiempo.collidepoint(pos_mous):
                            self.modo_juego = "tiempo"
                            self.tiempo_restante = 60.0
                            self.seleccionar_modo = False
                            self.generar_piezas()
                            self.sonidos.reproducir_musica()
                        elif self.btn_modo_puzle.collidepoint(pos_mous):
                            self.seleccionar_puzle = True
                        elif self.btn_logros_menu.collidepoint(pos_mous):
                            self.mostrando_logros = True
                        elif self.btn_ayuda_menu.collidepoint(pos_mous):
                            self.mostrando_ayuda = True
                    continue

                if self.pidiendo_nombre:
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_RETURN and len(self.nombre_jugador) > 0:
                            self.guardar_record_actual()
                        elif evento.key == pygame.K_BACKSPACE:
                            self.nombre_jugador = self.nombre_jugador[:-1]
                        elif len(self.nombre_jugador) < 4 and evento.unicode.isalpha():
                            self.nombre_jugador += evento.unicode.upper()
                    continue

                if self.mostrando_records:
                    if evento.type == pygame.MOUSEBUTTONDOWN:
                        self.__init__()
                    continue

                # --- EVENTOS DENTRO DEL JUEGO CON COMPATIBILIDAD TÁCTIL ---
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:
                        self.tiempo_inicio_toque = pygame.time.get_ticks()
                        self.pos_inicio_toque = pos_mous

                        if self.btn_undo.collidepoint(pos_mous):
                            self.ejecutar_deshacer()
                            continue
                        elif self.btn_logros_hud.collidepoint(pos_mous):
                            self.mostrando_logros = True
                            continue
                        elif self.btn_top10.collidepoint(pos_mous):
                            self.mostrando_records = True
                            continue
                        elif self.btn_ayuda.collidepoint(pos_mous):
                            self.mostrando_ayuda = True
                            continue
                        elif self.btn_menu_hud.collidepoint(pos_mous):
                            self.mostrando_menu_pausa = True
                            if self.pieza_seleccionada:
                                self.pieza_seleccionada.reset_pos()
                                self.pieza_seleccionada = None
                            continue

                        # HOLD
                        if self.zone_hold.collidepoint(pos_mous) and self.pieza_reserva is not None:
                            self.pieza_seleccionada = self.pieza_reserva
                            self.origen_seleccion = "hold"
                            self.pieza_seleccionada.arrastrando = True
                            
                            an, al = self.pieza_seleccionada.obtener_ancho_alto(escala=1.0)
                            self.drag_offset_x = an / 2
                            self.drag_offset_y = al + 50  # Offset vertical para que el dedo no tape la pieza
                            self.pieza_seleccionada.x = pos_mous[0] - self.drag_offset_x
                            self.pieza_seleccionada.y = pos_mous[1] - self.drag_offset_y
                            continue

                        # BANDEJA
                        for pieza in self.piezas_disponibles:
                            rects = pieza.obtener_rects(escala=pieza.escala_preview, inflar=12)
                            if any(r.collidepoint(pos_mous) for r in rects):
                                self.pieza_seleccionada = pieza
                                self.origen_seleccion = "bandeja"
                                pieza.arrastrando = True
                                
                                an, al = pieza.obtener_ancho_alto(escala=1.0)
                                self.drag_offset_x = an / 2
                                self.drag_offset_y = al + 50  # Offset vertical para visualización limpia en táctil
                                pieza.x = pos_mous[0] - self.drag_offset_x
                                pieza.y = pos_mous[1] - self.drag_offset_y
                                break

                    elif evento.button == 3: # ROTAR EN PC
                        if self.pieza_seleccionada:
                            self.pieza_seleccionada.rotar()
                            self.sonidos.play_rotar()
                        else:
                            for pieza in self.piezas_disponibles:
                                rects = pieza.obtener_rects(escala=pieza.escala_preview, inflar=12)
                                if any(r.collidepoint(pos_mous) for r in rects):
                                    pieza.rotar()
                                    self.sonidos.play_rotar()
                                    break

                elif evento.type == pygame.MOUSEBUTTONUP:
                    if evento.button == 1:
                        duracion_toque = pygame.time.get_ticks() - self.tiempo_inicio_toque
                        distancia_movida = math.hypot(
                            pos_mous[0] - self.pos_inicio_toque[0],
                            pos_mous[1] - self.pos_inicio_toque[1]
                        )

                        # Detección de TOQUE BREVE (TAP): Menos de 200ms y menos de 10px recorridos
                        es_tap = duracion_toque < 200 and distancia_movida < 10

                        if self.pieza_seleccionada:
                            pieza = self.pieza_seleccionada
                            col, fila = self.x_y_a_grid(pieza.x, pieza.y)

                            if col is not None and fila is not None and self.puede_colocar(pieza, col, fila):
                                self.colocar_pieza(pieza, col, fila)
                            elif es_tap:
                                pieza.rotar()
                                self.sonidos.play_rotar()
                                pieza.reset_pos()
                            elif self.zone_hold.collidepoint(pos_mous):
                                if self.origen_seleccion == "bandeja":
                                    if self.pieza_reserva is None:
                                        self.guardar_en_hold(pieza)
                                    else:
                                        pieza.reset_pos()
                                else:
                                    pieza.reset_pos()
                            elif self.origen_seleccion == "hold" and self.zone_bandeja.collidepoint(pos_mous):
                                if len(self.piezas_disponibles) < 3:
                                    slots_usados = {p.slot_index for p in self.piezas_disponibles}
                                    slot_libre = next(i for i in range(3) if i not in slots_usados)
                                    pieza.slot_index = slot_libre
                                    pieza.pos_origen_x = POS_TABLERO_X + 20 + slot_libre * 125
                                    pieza.pos_origen_y = 660
                                    pieza.reset_pos()
                                    self.piezas_disponibles.append(pieza)
                                    self.pieza_reserva = None
                                    self.sonidos.play_rotar()
                                else:
                                    pieza.reset_pos()
                            else:
                                pieza.reset_pos()

                            self.pieza_seleccionada = None
                            self.origen_seleccion = None

                        elif es_tap:
                            for pieza in self.piezas_disponibles:
                                rects = pieza.obtener_rects(escala=pieza.escala_preview, inflar=12)
                                if any(r.collidepoint(pos_mous) for r in rects):
                                    pieza.rotar()
                                    self.sonidos.play_rotar()
                                    break

                elif evento.type == pygame.MOUSEMOTION and self.pieza_seleccionada:
                    self.pieza_seleccionada.x = pos_mous[0] - self.drag_offset_x
                    self.pieza_seleccionada.y = pos_mous[1] - self.drag_offset_y

            # --- DIBUJAR EN SUPERFICIE VIRTUAL ---
            self.pantalla.fill(COLOR_FONDO)
            surf_juego = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL))
            surf_juego.fill(COLOR_FONDO)

            if self.seleccionar_puzle:
                t_tit = self.fuente_titulo.render("SELECCIONA PUZLE", True, COLOR_DORADO)
                self.pantalla.blit(t_tit, (ANCHO_VIRTUAL // 2 - t_tit.get_width() // 2, 130))
                for idx, cfg in enumerate(NIVELES_PUZLE):
                    r_btn = pygame.Rect(ANCHO_VIRTUAL // 2 - 140, 220 + idx * 70, 280, 55)
                    self.dibujar_boton_decorado(r_btn, cfg["nombre"], (37, 99, 235), COLOR_DORADO, pos_mous)
                self.renderizar_pantalla_escalada()
                continue

            if self.seleccionar_modo:
                for pf in self.piezas_fondo_menu:
                    pf["y"] += pf["vy"]
                    if pf["y"] > ALTO_VIRTUAL + 40:
                        pf["y"] = random.randint(-120, -40)
                        pf["x"] = random.randint(10, ANCHO_VIRTUAL - 70)
                        pf["color"] = random.choice(COLORES_PIEZAS)

                    tam_cel = int(22 * pf["escala"])
                    for bx, by in pf["forma"]:
                        rx = pf["x"] + bx * (tam_cel + 2)
                        ry = pf["y"] + by * (tam_cel + 2)
                        rect_p = pygame.Rect(rx, ry, tam_cel, tam_cel)
                        pygame.draw.rect(self.pantalla, pf["color"], rect_p, border_radius=4)
                        pygame.draw.rect(self.pantalla, (10, 15, 25), rect_p, width=1, border_radius=4)

                surf_marco = pygame.Surface((ANCHO_VIRTUAL - 50, ALTO_VIRTUAL - 40), pygame.SRCALPHA)
                pygame.draw.rect(surf_marco, (25, 35, 55, 200), surf_marco.get_rect(), border_radius=20)
                pygame.draw.rect(surf_marco, COLOR_DORADO, surf_marco.get_rect(), width=3, border_radius=20)
                self.pantalla.blit(surf_marco, (25, 20))

                pulso = math.sin(t_anim * 0.003) * 0.05 + 1.0
                texto_tit = "BLOCK DESTROYER"
                f_tit = pygame.font.SysFont("arial", int(36 * pulso), bold=True)

                s_glow = f_tit.render(texto_tit, True, (120, 80, 255))
                s_glow.set_alpha(100)
                for dx, dy in [(-3,0), (3,0), (0,-3), (0,3), (-2,-2), (2,2)]:
                    self.pantalla.blit(s_glow, (ANCHO_VIRTUAL // 2 - s_glow.get_width() // 2 + dx, 70 + dy))

                s_som = f_tit.render(texto_tit, True, (10, 10, 15))
                self.pantalla.blit(s_som, (ANCHO_VIRTUAL // 2 - s_som.get_width() // 2 + 4, 74))

                s_main = f_tit.render(texto_tit, True, COLOR_DORADO)
                self.pantalla.blit(s_main, (ANCHO_VIRTUAL // 2 - s_main.get_width() // 2, 70))

                rect_badge = pygame.Rect(ANCHO_VIRTUAL // 2 - 80, 135, 160, 28)
                pygame.draw.rect(self.pantalla, (20, 25, 40), rect_badge, border_radius=14)
                pygame.draw.rect(self.pantalla, COLOR_DORADO, rect_badge, width=2, border_radius=14)
                
                t_sub = self.fuente_peque.render("EDICIÓN DELUXE", True, (200, 225, 255))
                self.pantalla.blit(t_sub, (rect_badge.centerx - t_sub.get_width() // 2, rect_badge.centery - t_sub.get_height() // 2))

                if self.hay_partida_guardada():
                    self.dibujar_boton_decorado(self.btn_continuar, "▶ Continuar Partida", (16, 185, 129), COLOR_DORADO, pos_mous)

                self.dibujar_boton_decorado(self.btn_modo_clasico, "🎮 Modo Clásico", (37, 99, 235), COLOR_DORADO, pos_mous)
                self.dibujar_boton_decorado(self.btn_modo_tiempo, "⏱ Contrarreloj (60s)", (220, 38, 38), (255, 100, 100), pos_mous)
                self.dibujar_boton_decorado(self.btn_modo_puzle, "🧩 Modo Puzle", (147, 51, 234), (200, 100, 255), pos_mous)
                self.dibujar_boton_decorado(self.btn_logros_menu, "🏆 Ver Logros", (234, 179, 8), COLOR_DORADO, pos_mous)
                self.dibujar_boton_decorado(self.btn_ayuda_menu, "❓ Ayuda y Reglas", (30, 41, 59), (100, 116, 139), pos_mous)

                if self.mostrando_logros:
                    self.dibujar_pantalla_logros()
                elif self.mostrando_ayuda:
                    self.dibujar_pantalla_ayuda(t_anim)

                self.renderizar_pantalla_escalada()
                continue

            # HUD EN JUEGO
            max_puntos = self.high_scores[0]["score"] if self.high_scores else 0
            txt_puntos = self.fuente.render(f"Puntos: {self.puntuacion}", True, COLOR_TEXTO)
            txt_max = self.fuente.render(f"Máx: {max_puntos}", True, COLOR_DORADO)
            surf_juego.blit(txt_puntos, (POS_TABLERO_X, 15))
            surf_juego.blit(txt_max, (POS_TABLERO_X, 40))

            if self.modo_juego == "tiempo":
                color_rel = (239, 68, 68) if self.tiempo_restante < 10 else COLOR_TEXTO
                txt_time = self.fuente_grande.render(f"⏱ {self.tiempo_restante:.1f}s", True, color_rel)
                surf_juego.blit(txt_time, (POS_TABLERO_X, 70))
            elif self.modo_juego == "puzle":
                txt_puz = self.fuente.render(f"Puzle {self.nivel_puzle_actual + 1}", True, COLOR_DORADO)
                surf_juego.blit(txt_puz, (POS_TABLERO_X, 70))

            bot_cfg = [
                (self.btn_logros_hud, "🏆 Logros", COLOR_DORADO),
                (self.btn_top10, "🥇 Top 10", COLOR_DORADO),
                (self.btn_ayuda, "❓ Ayuda", (59, 130, 246)),
                (self.btn_menu_hud, "🏠 Menú", (234, 179, 8))
            ]
            for btn_r, txt_b, col_b in bot_cfg:
                pygame.draw.rect(surf_juego, COLOR_BOTON, btn_r, border_radius=6)
                pygame.draw.rect(surf_juego, col_b, btn_r, width=2, border_radius=6)
                t_lbl = self.fuente_peque.render(txt_b, True, COLOR_TEXTO)
                surf_juego.blit(t_lbl, (btn_r.centerx - t_lbl.get_width() // 2, btn_r.centery - t_lbl.get_height() // 2))

            # BOTÓN UNDO
            col_undo = (37, 99, 235) if self.undo_restantes > 0 else (60, 60, 70)
            pygame.draw.circle(surf_juego, col_undo, self.btn_undo.center, 22)
            pygame.draw.circle(surf_juego, COLOR_DORADO, self.btn_undo.center, 22, width=2)
            txt_undo = self.fuente_grande.render("↺", True, COLOR_TEXTO)
            surf_juego.blit(txt_undo, (self.btn_undo.centerx - txt_undo.get_width() // 2, self.btn_undo.centery - txt_undo.get_height() // 2 - 2))
            txt_u_cnt = self.fuente_micro.render(f"x{self.undo_restantes}", True, COLOR_DORADO)
            surf_juego.blit(txt_u_cnt, (self.btn_undo.centerx - txt_u_cnt.get_width() // 2, self.btn_undo.bottom + 2))

            # ZONA HOLD
            pygame.draw.rect(surf_juego, COLOR_TABLERO, self.zone_hold, border_radius=10)
            color_borde_hold = COLOR_DORADO if self.zone_hold.collidepoint(pos_mous) else COLOR_BOTON
            pygame.draw.rect(surf_juego, color_borde_hold, self.zone_hold, width=2, border_radius=10)
            txt_h = self.fuente_micro.render("HOLD", True, COLOR_DORADO)
            surf_juego.blit(txt_h, (self.zone_hold.centerx - txt_h.get_width() // 2, self.zone_hold.y + 5))
            
            if self.pieza_reserva and self.pieza_reserva != self.pieza_seleccionada:
                self.pieza_reserva.x = self.zone_hold.x + 6
                self.pieza_reserva.y = self.zone_hold.y + 30
                self.pieza_reserva.escala_preview = 0.35
                self.pieza_reserva.dibujar(surf_juego, self.fuente_micro, t_anim)

            # TABLERO DE JUEGO
            for f in range(8):
                for c in range(8):
                    x = POS_TABLERO_X + c * (TAMANO_CELDA + MARGEN)
                    y = POS_TABLERO_Y + f * (TAMANO_CELDA + MARGEN)
                    rect = pygame.Rect(x, y, TAMANO_CELDA, TAMANO_CELDA)
                    
                    cell = self.tablero[f][c]
                    if cell:
                        color_base = cell[0] if isinstance(cell, tuple) and isinstance(cell[0], tuple) else (cell if isinstance(cell, tuple) else COLOR_BOTON)
                        mult = cell[1] if isinstance(cell, tuple) and len(cell) == 2 and isinstance(cell[1], int) else 1
                        
                        pygame.draw.rect(surf_juego, color_base, rect, border_radius=6)
                        brillo = tuple(min(255, col + 70) for col in color_base)
                        pygame.draw.line(surf_juego, brillo, (rect.left + 2, rect.top + 2), (rect.right - 2, rect.top + 2), width=2)
                        pygame.draw.line(surf_juego, brillo, (rect.left + 2, rect.top + 2), (rect.left + 2, rect.bottom - 2), width=2)

                        if mult > 1:
                            pygame.draw.rect(surf_juego, COLOR_DORADO, rect, width=2, border_radius=6)
                            txt_m = self.fuente_micro.render(f"x{mult}", True, COLOR_DORADO)
                            surf_juego.blit(txt_m, (rect.centerx - txt_m.get_width() // 2, rect.centery - txt_m.get_height() // 2))
                    else:
                        pygame.draw.rect(surf_juego, COLOR_CASILLA_VACIA, rect, border_radius=6)

            # Previsualización al arrastrar
            if self.pieza_seleccionada:
                col, fila = self.x_y_a_grid(self.pieza_seleccionada.x, self.pieza_seleccionada.y)
                if col is not None and fila is not None and self.puede_colocar(self.pieza_seleccionada, col, fila):
                    for bx, by in self.pieza_seleccionada.forma:
                        x = POS_TABLERO_X + (col + bx) * (TAMANO_CELDA + MARGEN)
                        y = POS_TABLERO_Y + (fila + by) * (TAMANO_CELDA + MARGEN)
                        rect_prev = pygame.Rect(x, y, TAMANO_CELDA, TAMANO_CELDA)
                        pygame.draw.rect(surf_juego, (255, 255, 255, 140), rect_prev, border_radius=6, width=3)

            # PIEZAS EN BANDEJA
            for pieza in self.piezas_disponibles:
                if pieza != self.pieza_seleccionada:
                    pieza.x = pieza.pos_origen_x
                    pieza.y = pieza.pos_origen_y
                    pieza.escala_preview = 0.5
                    pieza.dibujar(surf_juego, self.fuente_micro, t_anim)

            if self.pieza_seleccionada:
                self.pieza_seleccionada.dibujar(surf_juego, self.fuente_micro, t_anim)

            # EFECTOS VISUALES
            for d in self.destellos[:]:
                d.actualizar(); d.dibujar(surf_juego)
                if d.vida <= 0: self.destellos.remove(d)

            for p in self.particulas[:]:
                p.actualizar(); p.dibujar(surf_juego)
                if p.vida <= 0: self.particulas.remove(p)

            for tf in self.textos_flotantes[:]:
                tf.actualizar(); tf.dibujar(surf_juego, self.fuente)
                if tf.vida <= 0: self.textos_flotantes.remove(tf)

            self.pantalla.blit(surf_juego, (shake_offset_x, shake_offset_y))

            for notif in self.notificaciones[:]:
                notif.actualizar()
                notif.dibujar(self.pantalla, self.fuente_peque)
                if notif.vida <= 0: self.notificaciones.remove(notif)

            # OVERLAYS / MODALES
            if self.mostrando_menu_pausa:
                s = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL)); s.set_alpha(220); s.fill((10, 14, 20))
                self.pantalla.blit(s, (0, 0))

                t_pausa = self.fuente_grande.render("PAUSA", True, COLOR_DORADO)
                self.pantalla.blit(t_pausa, (ANCHO_VIRTUAL // 2 - t_pausa.get_width() // 2, 180))

                self.dibujar_boton_decorado(self.btn_pausa_continuar, "▶ Continuar Partida", (37, 99, 235), COLOR_DORADO, pos_mous)
                self.dibujar_boton_decorado(self.btn_pausa_guardar, "💾 Guardar y Salir", (16, 185, 129), (100, 255, 180), pos_mous)
                self.dibujar_boton_decorado(self.btn_pausa_finalizar, "🏁 Finalizar Partida", (220, 38, 38), (255, 100, 100), pos_mous)

            elif self.mostrando_logros:
                self.dibujar_pantalla_logros()

            elif self.mostrando_ayuda:
                self.dibujar_pantalla_ayuda(t_anim)

            elif self.pidiendo_nombre:
                s = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL)); s.set_alpha(220); s.fill((0, 0, 0))
                self.pantalla.blit(s, (0, 0))
                t1 = self.fuente_grande.render("¡NUEVO RÉCORD!", True, COLOR_DORADO)
                t2 = self.fuente.render(f"Puntuación final: {self.puntuacion}", True, COLOR_TEXTO)
                nom_disp = self.nombre_jugador.ljust(4, "_")
                t_nom = self.fuente_grande.render(f" [ {nom_disp} ] ", True, COLOR_DORADO)
                t_enter = self.fuente.render("Presiona ENTER para guardar", True, (150, 150, 150))

                self.pantalla.blit(t1, (ANCHO_VIRTUAL // 2 - t1.get_width() // 2, 200))
                self.pantalla.blit(t2, (ANCHO_VIRTUAL // 2 - t2.get_width() // 2, 250))
                self.pantalla.blit(t_nom, (ANCHO_VIRTUAL // 2 - t_nom.get_width() // 2, 340))
                self.pantalla.blit(t_enter, (ANCHO_VIRTUAL // 2 - t_enter.get_width() // 2, 420))

            elif self.mostrando_records:
                s = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL)); s.set_alpha(235); s.fill((10, 14, 20))
                self.pantalla.blit(s, (0, 0))
                
                if self.victoria_puzle:
                    titulo_txt = "¡PUZLE RESUELTO!"
                    color_tit = COLOR_DORADO
                else:
                    titulo_txt = "GAME OVER" if self.game_over else "CLASIFICACIÓN"
                    color_tit = (239, 68, 68) if self.game_over else COLOR_TEXTO

                t_go = self.fuente_grande.render(titulo_txt, True, color_tit)
                t_top = self.fuente.render("--- TOP 10 MÁXIMAS ---", True, COLOR_DORADO)
                self.pantalla.blit(t_go, (ANCHO_VIRTUAL // 2 - t_go.get_width() // 2, 50))
                self.pantalla.blit(t_top, (ANCHO_VIRTUAL // 2 - t_top.get_width() // 2, 100))

                y_rec = 160
                if not self.high_scores:
                    t_vac = self.fuente.render("Sin récords aún", True, (150, 150, 150))
                    self.pantalla.blit(t_vac, (ANCHO_VIRTUAL // 2 - t_vac.get_width() // 2, y_rec))
                else:
                    for idx, item in enumerate(self.high_scores):
                        color_item = COLOR_DORADO if idx == 0 else COLOR_TEXTO
                        linea = f"{idx+1:2d}.  {item['name']}   -   {item['score']}"
                        t_lin = self.fuente.render(linea, True, color_item)
                        self.pantalla.blit(t_lin, (ANCHO_VIRTUAL // 2 - 100, y_rec))
                        y_rec += 32

                txt_footer = "Haz clic para volver al menú"
                t_rst = self.fuente.render(txt_footer, True, (150, 150, 150))
                self.pantalla.blit(t_rst, (ANCHO_VIRTUAL // 2 - t_rst.get_width() // 2, ALTO_VIRTUAL - 70))

            self.renderizar_pantalla_escalada()

    # --- PANTALLA DE LOGROS ---
    def dibujar_pantalla_logros(self):
        s = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL)); s.set_alpha(248); s.fill((10, 14, 24))
        self.pantalla.blit(s, (0, 0))

        t_tit = self.fuente_grande.render("PANEL DE LOGROS", True, COLOR_DORADO)
        self.pantalla.blit(t_tit, (ANCHO_VIRTUAL // 2 - t_tit.get_width() // 2, 35))

        pygame.draw.line(self.pantalla, COLOR_DORADO, (30, 80), (ANCHO_VIRTUAL - 30, 80), 2)

        y_pos = 100
        for logro in LOGROS_DEFINICION:
            desbloqueado = logro["id"] in self.logros_desbloqueados
            
            rect_card = pygame.Rect(30, y_pos, ANCHO_VIRTUAL - 60, 75)
            col_bg = (24, 34, 50) if desbloqueado else (18, 22, 30)
            col_borde = COLOR_DORADO if desbloqueado else (45, 55, 70)
            
            pygame.draw.rect(self.pantalla, col_bg, rect_card, border_radius=10)
            pygame.draw.rect(self.pantalla, col_borde, rect_card, width=2 if desbloqueado else 1, border_radius=10)

            icono = logro["icono"] if desbloqueado else "🔒"
            t_ico = self.fuente_grande.render(icono, True, COLOR_DORADO if desbloqueado else (100, 100, 100))
            self.pantalla.blit(t_ico, (rect_card.x + 15, rect_card.centery - t_ico.get_height() // 2))

            col_tit = COLOR_DORADO if desbloqueado else (140, 140, 140)
            t_nom = self.fuente.render(logro["titulo"], True, col_tit)
            self.pantalla.blit(t_nom, (rect_card.x + 65, rect_card.y + 12))

            t_desc = self.fuente_peque.render(logro["desc"], True, COLOR_TEXTO if desbloqueado else (100, 100, 100))
            self.pantalla.blit(t_desc, (rect_card.x + 65, rect_card.y + 40))

            if desbloqueado:
                t_check = self.fuente.render("✓", True, (34, 197, 94))
                self.pantalla.blit(t_check, (rect_card.right - 30, rect_card.centery - t_check.get_height() // 2))

            y_pos += 90

        t_rst = self.fuente.render("Haz clic en cualquier lugar para cerrar", True, (150, 150, 150))
        self.pantalla.blit(t_rst, (ANCHO_VIRTUAL // 2 - t_rst.get_width() // 2, ALTO_VIRTUAL - 55))

    # --- PANTALLA DE AYUDA ---
    def dibujar_pantalla_ayuda(self, t_anim):
        s = pygame.Surface((ANCHO_VIRTUAL, ALTO_VIRTUAL)); s.set_alpha(248); s.fill((10, 14, 24))
        self.pantalla.blit(s, (0, 0))

        t_tit = self.fuente_grande.render("GUÍA DEL JUEGO", True, COLOR_DORADO)
        self.pantalla.blit(t_tit, (ANCHO_VIRTUAL // 2 - t_tit.get_width() // 2, 25))

        pygame.draw.line(self.pantalla, COLOR_DORADO, (30, 65), (ANCHO_VIRTUAL - 30, 65), 2)
        t_ctrl = self.fuente.render("🎮 Controles Básicos:", True, COLOR_DORADO)
        self.pantalla.blit(t_ctrl, (30, 75))
        lines_ctrl = [
            "• Arrastrar y Soltar: Colocar fichas en el tablero.",
            "• Tap (Toque breve) / Clic Dcho: Rotar ficha 90°.",
            "• Tecla ESC / Botón Menú: Pausar / Menú Principal."
        ]
        for i, l in enumerate(lines_ctrl):
            self.pantalla.blit(self.fuente_peque.render(l, True, COLOR_TEXTO), (40, 102 + i * 20))

        t_mecanicas = self.fuente.render("🔄 Deshacer y Reserva (Hold):", True, COLOR_DORADO)
        self.pantalla.blit(t_mecanicas, (30, 170))
        
        pygame.draw.circle(self.pantalla, (37, 99, 235), (55, 215), 16)
        pygame.draw.circle(self.pantalla, COLOR_DORADO, (55, 215), 16, width=2)
        t_u_ico = self.fuente.render("↺", True, COLOR_TEXTO)
        self.pantalla.blit(t_u_ico, (55 - t_u_ico.get_width() // 2, 215 - t_u_ico.get_height() // 2 - 2))
        self.pantalla.blit(self.fuente_peque.render("Deshacer (↺): Revierte tu último movimiento (Máx 3).", True, COLOR_TEXTO), (85, 205))

        r_h = pygame.Rect(40, 240, 30, 35)
        pygame.draw.rect(self.pantalla, COLOR_TABLERO, r_h, border_radius=5)
        pygame.draw.rect(self.pantalla, COLOR_DORADO, r_h, width=2, border_radius=5)
        self.pantalla.blit(self.fuente_micro.render("HOLD", True, COLOR_DORADO), (42, 242))
        self.pantalla.blit(self.fuente_peque.render("Reserva (HOLD): Guarda 1 ficha. Arrástrala al tablero o a la bandeja.", True, COLOR_TEXTO), (85, 248))

        t_bloques = self.fuente.render("🧩 Bloques Especiales:", True, COLOR_DORADO)
        self.pantalla.blit(t_bloques, (30, 290))

        r_m = pygame.Rect(40, 320, 32, 32)
        pygame.draw.rect(self.pantalla, (234, 179, 8), r_m, border_radius=6)
        pygame.draw.rect(self.pantalla, COLOR_DORADO, r_m, width=2, border_radius=6)
        t_x2 = self.fuente_micro.render("x3", True, COLOR_DORADO)
        self.pantalla.blit(t_x2, (r_m.centerx - t_x2.get_width() // 2, r_m.centery - t_x2.get_height() // 2))
        self.pantalla.blit(self.fuente_peque.render("Multiplicador (x2 / x3): Duplica o triplica los puntos.", True, COLOR_TEXTO), (85, 325))

        r_b = pygame.Rect(40, 360, 32, 32)
        pygame.draw.rect(self.pantalla, (80, 80, 80), r_b, border_radius=6)
        pygame.draw.circle(self.pantalla, (255, 60, 0), r_b.center, 5)
        self.pantalla.blit(self.fuente_peque.render("Bomba 💣: Explota destruyendo un área de 3x3.", True, COLOR_TEXTO), (85, 365))

        r_a = pygame.Rect(40, 400, 32, 32)
        r_c = int((math.sin(t_anim * 0.005) + 1) * 127)
        pygame.draw.rect(self.pantalla, (r_c, 150, 255), r_a, border_radius=6)
        self.pantalla.blit(self.fuente_peque.render("Arcoíris 🌈: Limpia toda la fila y columna al instante.", True, COLOR_TEXTO), (85, 405))

        pygame.draw.line(self.pantalla, COLOR_DORADO, (30, 445), (ANCHO_VIRTUAL - 30, 445), 2)
        t_mod = self.fuente.render("🏆 Modos y Logros:", True, COLOR_DORADO)
        self.pantalla.blit(t_mod, (30, 455))
        reglas = [
            "• Modo Clásico: Juega libremente hasta no tener espacio.",
            "• Contrarreloj: 60s iniciales. Cada línea suma +3s.",
            "• Modo Puzle: Despeja tableros fijos predefinidos.",
            "• Logros: Completa desafíos para desbloquear trofeos."
        ]
        for i, r in enumerate(reglas):
            self.pantalla.blit(self.fuente_peque.render(r, True, COLOR_TEXTO), (40, 485 + i * 20))

        t_rst = self.fuente.render("Haz clic en cualquier lugar para cerrar", True, (150, 150, 150))
        self.pantalla.blit(t_rst, (ANCHO_VIRTUAL // 2 - t_rst.get_width() // 2, ALTO_VIRTUAL - 45))

if __name__ == "__main__":
    JuegoBlockBlast().ejecutar()
