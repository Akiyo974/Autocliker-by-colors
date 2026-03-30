"""
Smart AutoClicker
-----------------
Détecte et clique automatiquement sur des zones d'une couleur choisie.

Dépendances :
    pip install opencv-python mss pyautogui numpy pynput

Utilisation :
    1. Lancez le script — une interface graphique s'ouvre.
    2. Choisissez jusqu'à 3 couleurs cibles (onglets Couleur 1/2/3).
    3. Ajustez les tolérances jusqu'à ce que la détection soit bonne.
    4. Dessinez la zone où chercher (optionnel — plein écran par défaut).
    5. Cliquez sur "Démarrer".
    6. Ctrl+Shift+S  → démarrer / arrêter depuis n'importe quelle fenêtre.
    7. Souris en haut-gauche = arrêt d'urgence (failsafe PyAutoGUI).

Options activables (section Options) :
    • Dark mode                  — thème sombre
    • Overlay de prévisualisation — fenêtre montrant les cibles détectées en temps réel
    • Variation de cadence       — CPM légèrement aléatoire (±20 %)
    • Micro-déplacement          — décalage aléatoire du point de clic (±jitter px)
    • Délai de démarrage         — attendre N secondes avant le premier clic
    • Pauses aléatoires          — pauses courtes et imprévisibles entre les clics
"""

import time
import random
import threading
import tkinter as tk
from tkinter import ttk, colorchooser

import cv2
import mss
import numpy as np
import pyautogui
from pynput import keyboard as kb

# ── Thèmes ─────────────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "bg":         "#f0f0f0",
        "fg":         "#1a1a1a",
        "frame_bg":   "#f0f0f0",
        "entry_bg":   "#ffffff",
        "btn_bg":     "#e0e0e0",
        "status_bg":  "#d8d8d8",
        "accent":     "#0078d4",
    },
    "dark": {
        "bg":         "#1e1e2e",
        "fg":         "#cdd6f4",
        "frame_bg":   "#313244",
        "entry_bg":   "#45475a",
        "btn_bg":     "#585b70",
        "status_bg":  "#181825",
        "accent":     "#89b4fa",
    },
}

# ── État global ────────────────────────────────────────────────────────────────

running   = False
zone_lock = threading.Lock()
ZONE      = {"left": 0, "top": 0, "width": 1920, "height": 1080}

# ── Détection ─────────────────────────────────────────────────────────────────

def rgb_to_hsv_cv(r: int, g: int, b: int):
    """RGB 0-255 → H(0-180) S(0-255) V(0-255) format OpenCV."""
    px  = np.array([[[b, g, r]]], dtype=np.uint8)
    hsv = cv2.cvtColor(px, cv2.COLOR_BGR2HSV)
    return int(hsv[0, 0, 0]), int(hsv[0, 0, 1]), int(hsv[0, 0, 2])


def build_hsv_range(h: int, s: int, v: int, tol_h: int, tol_sv: int):
    """Retourne (low, high) numpy uint8 pour cv2.inRange."""
    h_low  = max(0,   h - tol_h)
    h_high = min(180, h + tol_h)
    s_low  = max(0,   s - tol_sv)
    v_low  = max(0,   v - tol_sv)
    low  = np.array([h_low,  s_low, v_low], dtype=np.uint8)
    high = np.array([h_high, 255,   255  ], dtype=np.uint8)
    return low, high


def detect_targets(frame_bgr: np.ndarray, low, high, min_radius: int):
    """Retourne la liste des centres (x, y) des taches de couleur détectées."""
    hsv    = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask   = cv2.inRange(hsv, low, high)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
    mask   = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    for cnt in contours:
        if cv2.contourArea(cnt) < np.pi * min_radius ** 2:
            continue
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        centers.append((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
    return centers

# ── Overlay de prévisualisation ────────────────────────────────────────────────

class PreviewOverlay:
    """Fenêtre OpenCV affichant les cibles détectées en temps réel."""

    def __init__(self):
        self._lock   = threading.Lock()
        self._frame  = None
        self._active = False
        self._thread = None

    def start(self):
        if self._active:
            return
        self._active = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._active = False

    def push(self, frame_bgr: np.ndarray, centers: list, region: dict):
        """Reçoit une frame BGR avec les centres détectés pour affichage."""
        vis = frame_bgr.copy()
        for (cx, cy) in centers:
            cv2.circle(vis, (cx, cy), 12, (0, 255, 0), 2)
            cv2.drawMarker(vis, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
        # Redimensionner pour ne pas déborder
        h, w = vis.shape[:2]
        max_w, max_h = 640, 360
        scale = min(max_w / max(w, 1), max_h / max(h, 1), 1.0)
        if scale < 1.0:
            vis = cv2.resize(vis, (int(w * scale), int(h * scale)))
        with self._lock:
            self._frame = vis

    def _run(self):
        cv2.namedWindow("Prévisualisation", cv2.WINDOW_NORMAL)
        while self._active:
            with self._lock:
                frame = self._frame
            if frame is not None:
                cv2.imshow("Prévisualisation", frame)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                self._active = False
                break
        cv2.destroyWindow("Prévisualisation")

# ── Boucle de clic ─────────────────────────────────────────────────────────────

def clicker_loop(app: "App"):
    global running
    pyautogui.PAUSE    = 0
    pyautogui.FAILSAFE = True

    clicked_total = 0
    t_start       = time.perf_counter()
    last_click_t  = 0.0
    use_timer     = app.get_timer_enabled()
    timer_end     = t_start + app.get_timer_seconds() if use_timer else None
    pos_cooldown: dict = {}
    COOLDOWN_RADIUS = 20

    # ── Options naturalité ─────────────────────────────────────────────────────
    opt_cpm_variation  = app.get_opt("cpm_variation")
    opt_jitter         = app.get_opt("jitter")
    jitter_px          = app.get_jitter_px()
    opt_start_delay    = app.get_opt("start_delay")
    start_delay_s      = app.get_start_delay()
    opt_random_pauses  = app.get_opt("random_pauses")
    opt_preview        = app.get_opt("preview")

    # ── Overlay preview ────────────────────────────────────────────────────────
    preview = None
    if opt_preview:
        preview = PreviewOverlay()
        preview.start()

    # ── Délai de démarrage ─────────────────────────────────────────────────────
    if opt_start_delay and start_delay_s > 0:
        for remaining in range(start_delay_s, 0, -1):
            if not running:
                if preview:
                    preview.stop()
                return
            app.after(0, lambda r=remaining: app._set_status(
                f"Démarrage dans {r}s…"))
            time.sleep(1)

    def is_on_cooldown(cx, cy, cooldown_s):
        now = time.perf_counter()
        for (px, py), t in list(pos_cooldown.items()):
            if abs(cx - px) < COOLDOWN_RADIUS and abs(cy - py) < COOLDOWN_RADIUS:
                if now - t < cooldown_s:
                    return True
                else:
                    del pos_cooldown[(px, py)]
        return False

    # Compteur de clics pour les pauses aléatoires
    clicks_since_pause = 0
    next_pause_at      = random.randint(8, 20) if opt_random_pauses else 999999

    with mss.mss() as sct:
        while running:
            with zone_lock:
                region = dict(ZONE)

            if timer_end is not None:
                remaining = timer_end - time.perf_counter()
                if remaining <= 0:
                    running = False
                    break
                app.after(0, lambda r=remaining: app._set_status(
                    f"En cours…  ⏱ {int(r)}s restantes"))

            # Récupérer les couleurs actives (1 à 3)
            colors      = app.get_active_colors()
            min_r       = app.get_min_radius()
            cpm         = max(1, app.get_cpm())
            if opt_cpm_variation:
                cpm = cpm * random.uniform(0.80, 1.20)
            interval    = 60.0 / cpm
            miss_rate   = app.get_miss_rate()
            cooldown_s  = app.get_cooldown()

            raw       = sct.grab(region)
            frame_rgb = np.frombuffer(raw.rgb, dtype=np.uint8).reshape(raw.height, raw.width, 3)
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # Fusionner les cibles de toutes les couleurs actives
            all_centers = []
            for (rgb, tol_h, tol_sv) in colors:
                h, s, v   = rgb_to_hsv_cv(*rgb)
                low, high = build_hsv_range(h, s, v, tol_h, tol_sv)
                all_centers.extend(detect_targets(frame_bgr, low, high, min_r))

            if preview:
                preview.push(frame_bgr, all_centers, region)

            for (cx, cy) in all_centers:
                if not running:
                    break

                if cooldown_s > 0 and is_on_cooldown(cx, cy, cooldown_s):
                    continue

                wait = interval - (time.perf_counter() - last_click_t)
                if wait > 0:
                    time.sleep(wait)
                if not running:
                    break

                if random.random() < miss_rate:
                    last_click_t = time.perf_counter()
                    pos_cooldown[(cx, cy)] = last_click_t
                    continue

                # Micro-déplacement aléatoire
                click_x = region["left"] + cx
                click_y = region["top"]  + cy
                if opt_jitter and jitter_px > 0:
                    click_x += random.randint(-jitter_px, jitter_px)
                    click_y += random.randint(-jitter_px, jitter_px)

                pyautogui.click(click_x, click_y)
                last_click_t = time.perf_counter()
                pos_cooldown[(cx, cy)] = last_click_t
                clicked_total         += 1
                clicks_since_pause    += 1

                # Pauses aléatoires
                if opt_random_pauses and clicks_since_pause >= next_pause_at:
                    pause_dur          = random.uniform(0.3, 1.5)
                    clicks_since_pause = 0
                    next_pause_at      = random.randint(8, 20)
                    time.sleep(pause_dur)

    if preview:
        preview.stop()

    elapsed = time.perf_counter() - t_start
    cps     = clicked_total / elapsed if elapsed > 0 else 0
    app.after(0, lambda: app.on_clicker_stopped(clicked_total, cps))

# ── Interface graphique ────────────────────────────────────────────────────────

class ColorSlot:
    """Un slot couleur : rgb, hsv, tol_h, tol_sv, actif."""

    def __init__(self, rgb=(255, 140, 0), active=True):
        self.rgb    = rgb
        self.hsv    = rgb_to_hsv_cv(*rgb)
        self.active = active
        self.var_tol_h  = tk.IntVar(value=15)
        self.var_tol_sv = tk.IntVar(value=60)


class App(tk.Tk):
    _PAD       = 10
    _N_COLORS  = 3  # nombre maximum de couleurs simultanées

    def __init__(self):
        super().__init__()
        self.title("Smart AutoClicker")
        self.resizable(False, False)

        # ── Slots couleur ──────────────────────────────────────────────────────
        self._slots = [
            ColorSlot((255, 140, 0), active=True),   # orange par défaut
            ColorSlot((0,   200, 80), active=False),  # vert (désactivé)
            ColorSlot((50,  120, 255), active=False), # bleu (désactivé)
        ]

        # ── Variables options ──────────────────────────────────────────────────
        self.var_dark_mode      = tk.BooleanVar(value=False)
        self.var_opt_preview    = tk.BooleanVar(value=False)
        self.var_opt_cpm_var    = tk.BooleanVar(value=False)
        self.var_opt_jitter     = tk.BooleanVar(value=False)
        self.var_jitter_px      = tk.IntVar(value=5)
        self.var_opt_start_d    = tk.BooleanVar(value=False)
        self.var_start_delay    = tk.StringVar(value="3")
        self.var_opt_pauses     = tk.BooleanVar(value=False)

        self._current_theme = "light"

        self._build_ui()
        self._refresh_all_color_previews()
        self._refresh_zone_label()
        self._start_hotkey_listener()

    # ── Getters thread-safe ────────────────────────────────────────────────────

    def get_active_colors(self):
        """Retourne [(rgb, tol_h, tol_sv), ...] pour les slots actifs."""
        result = []
        for slot in self._slots:
            if slot.active:
                result.append((slot.rgb, slot.var_tol_h.get(), slot.var_tol_sv.get()))
        return result if result else [(self._slots[0].rgb,
                                       self._slots[0].var_tol_h.get(),
                                       self._slots[0].var_tol_sv.get())]

    def get_tol_h(self):      return self._slots[0].var_tol_h.get()
    def get_tol_sv(self):     return self._slots[0].var_tol_sv.get()
    def get_min_radius(self): return self.var_radius.get()
    def get_cpm(self):        return self.var_cpm.get()
    def get_miss_rate(self):  return self.var_miss.get() / 100.0
    def get_timer_enabled(self): return self.var_timer_on.get()
    def get_timer_seconds(self):
        try:    return max(1, int(self.var_timer_val.get()))
        except: return 60
    def get_cooldown(self):
        try:    return max(0, float(self.var_cooldown.get())) / 1000.0
        except: return 0.3
    def get_opt(self, key: str) -> bool:
        return {
            "preview":       self.var_opt_preview.get(),
            "cpm_variation": self.var_opt_cpm_var.get(),
            "jitter":        self.var_opt_jitter.get(),
            "start_delay":   self.var_opt_start_d.get(),
            "random_pauses": self.var_opt_pauses.get(),
        }[key]
    def get_jitter_px(self):
        return self.var_jitter_px.get()
    def get_start_delay(self):
        try:    return max(0, int(self.var_start_delay.get()))
        except: return 3

    # ── Callback fin de session ────────────────────────────────────────────────

    def on_clicker_stopped(self, total: int, cps: float):
        global running
        running = False
        self.btn_toggle.config(text="▶  Démarrer", state="normal")
        self._set_status(f"Arrêté — {total} clics  ({cps:.1f} clics/s)")

    # ── Construction de l'UI ───────────────────────────────────────────────────

    def _build_ui(self):
        P = self._PAD

        # ── Notebook multi-couleurs ────────────────────────────────────────────
        frm_colors = ttk.LabelFrame(self, text=" Couleurs cibles ", padding=P)
        frm_colors.grid(row=0, column=0, padx=P, pady=(P, 4), sticky="ew")

        self._nb_colors = ttk.Notebook(frm_colors)
        self._nb_colors.pack(fill="both")

        self._color_tabs = []
        labels = ["Couleur 1", "Couleur 2", "Couleur 3"]
        for i, slot in enumerate(self._slots):
            tab = ttk.Frame(self._nb_colors, padding=(P // 2))
            self._nb_colors.add(tab, text=labels[i])
            self._build_color_tab(tab, i)
            self._color_tabs.append(tab)

        # ── Section zone ───────────────────────────────────────────────────────
        frm_zone = ttk.LabelFrame(self, text=" Zone de detection ", padding=P)
        frm_zone.grid(row=1, column=0, padx=P, pady=4, sticky="ew")

        self.lbl_zone = ttk.Label(frm_zone, text="")
        self.lbl_zone.grid(row=0, column=0, sticky="w")
        ttk.Button(frm_zone, text="Dessiner la zone…",
                   command=self._pick_zone).grid(row=0, column=1, padx=(10, 0))
        ttk.Button(frm_zone, text="Plein ecran",
                   command=self._reset_zone).grid(row=0, column=2, padx=(4, 0))

        # ── Section paramètres ─────────────────────────────────────────────────
        frm_par = ttk.LabelFrame(self, text=" Parametres ", padding=P)
        frm_par.grid(row=2, column=0, padx=P, pady=4, sticky="ew")

        ttk.Label(frm_par, text="Rayon min (px) :").grid(row=0, column=0, sticky="w")
        self.var_radius = tk.IntVar(value=8)
        ttk.Spinbox(frm_par, from_=1, to=200, textvariable=self.var_radius,
                    width=6).grid(row=0, column=1, sticky="w", padx=4)

        ttk.Label(frm_par, text="Clics / minute :").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.var_cpm = tk.IntVar(value=120)
        self.lbl_cpm = ttk.Label(frm_par, text="120", width=5)
        ttk.Scale(frm_par, variable=self.var_cpm, from_=1, to=6000,
                  orient="horizontal", length=220,
                  command=lambda v: self.lbl_cpm.config(
                      text=str(int(float(v))))).grid(row=1, column=1, sticky="w", pady=(4, 0))
        self.lbl_cpm.grid(row=1, column=2, padx=(4, 0))

        ttk.Label(frm_par, text="Taux d'erreur (%) :").grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.var_miss = tk.IntVar(value=5)
        self.lbl_miss = ttk.Label(frm_par, text="5 %", width=5)
        ttk.Scale(frm_par, variable=self.var_miss, from_=0, to=80,
                  orient="horizontal", length=220,
                  command=lambda v: self.lbl_miss.config(
                      text=f"{int(float(v))} %")).grid(row=2, column=1, sticky="w", pady=(4, 0))
        self.lbl_miss.grid(row=2, column=2, padx=(4, 0))

        ttk.Label(frm_par, text="Cooldown cible (ms) :").grid(row=3, column=0, sticky="w", pady=(4, 0))
        self.var_cooldown = tk.StringVar(value="300")
        ttk.Spinbox(frm_par, from_=0, to=10000, textvariable=self.var_cooldown,
                    width=7).grid(row=3, column=1, sticky="w", padx=4, pady=(4, 0))
        ttk.Label(frm_par, text="ms").grid(row=3, column=2, sticky="w", padx=(0, 4))

        # Timer
        frm_timer = ttk.Frame(frm_par)
        frm_timer.grid(row=4, column=0, columnspan=3, sticky="w", pady=(6, 0))
        self.var_timer_on  = tk.BooleanVar(value=False)
        self.var_timer_val = tk.StringVar(value="60")
        ttk.Checkbutton(frm_timer, text="Arrêter après",
                        variable=self.var_timer_on,
                        command=self._refresh_timer_state).pack(side="left")
        self.spn_timer = ttk.Spinbox(frm_timer, from_=1, to=86400,
                                     textvariable=self.var_timer_val,
                                     width=7, state="disabled")
        self.spn_timer.pack(side="left", padx=4)
        ttk.Label(frm_timer, text="secondes").pack(side="left")

        # ── Section options activables ─────────────────────────────────────────
        frm_opts = ttk.LabelFrame(self, text=" Options ", padding=P)
        frm_opts.grid(row=3, column=0, padx=P, pady=4, sticky="ew")

        # Dark mode
        ttk.Checkbutton(frm_opts, text="Dark mode",
                        variable=self.var_dark_mode,
                        command=self._toggle_theme).grid(
            row=0, column=0, sticky="w")

        # Overlay preview
        ttk.Checkbutton(frm_opts, text="Overlay prévisualisation (fenêtre OpenCV)",
                        variable=self.var_opt_preview).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(2, 0))

        # Variation CPM
        ttk.Checkbutton(frm_opts, text="Variation de cadence (±20 % aléatoire)",
                        variable=self.var_opt_cpm_var).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))

        # Micro-déplacement
        frm_jitter = ttk.Frame(frm_opts)
        frm_jitter.grid(row=3, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ttk.Checkbutton(frm_jitter, text="Micro-déplacement aléatoire  ±",
                        variable=self.var_opt_jitter,
                        command=self._refresh_jitter_state).pack(side="left")
        self.spn_jitter = ttk.Spinbox(frm_jitter, from_=1, to=50,
                                      textvariable=self.var_jitter_px,
                                      width=4, state="disabled")
        self.spn_jitter.pack(side="left", padx=2)
        ttk.Label(frm_jitter, text="px").pack(side="left")

        # Délai de démarrage
        frm_sdel = ttk.Frame(frm_opts)
        frm_sdel.grid(row=4, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ttk.Checkbutton(frm_sdel, text="Délai de démarrage",
                        variable=self.var_opt_start_d,
                        command=self._refresh_startdelay_state).pack(side="left")
        self.spn_start_delay = ttk.Spinbox(frm_sdel, from_=1, to=300,
                                           textvariable=self.var_start_delay,
                                           width=5, state="disabled")
        self.spn_start_delay.pack(side="left", padx=(4, 2))
        ttk.Label(frm_sdel, text="secondes").pack(side="left")

        # Pauses aléatoires
        ttk.Checkbutton(frm_opts, text="Pauses aléatoires (0.3–1.5 s toutes les 8–20 clics)",
                        variable=self.var_opt_pauses).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(2, 0))

        # ── Contrôles ──────────────────────────────────────────────────────────
        frm_ctrl = ttk.Frame(self)
        frm_ctrl.grid(row=4, column=0, padx=P, pady=P, sticky="ew")
        frm_ctrl.columnconfigure(0, weight=1)

        self.btn_toggle = ttk.Button(frm_ctrl, text="▶  Démarrer",
                                     command=self._toggle)
        self.btn_toggle.grid(row=0, column=0, sticky="ew")

        # ── Statut ─────────────────────────────────────────────────────────────
        self.lbl_status = ttk.Label(self, text="Prêt.  |  Raccourci : Ctrl+Shift+S",
                                    anchor="w", relief="sunken", padding=(4, 2))
        self.lbl_status.grid(row=5, column=0, padx=P, pady=(0, P), sticky="ew")

    def _build_color_tab(self, parent, index: int):
        """Construit le contenu d'un onglet couleur."""
        slot = self._slots[index]
        P    = 4

        # Activer / désactiver le slot (slot 0 toujours actif)
        var_active = tk.BooleanVar(value=slot.active)

        def toggle_active():
            slot.active = var_active.get()

        if index > 0:
            ttk.Checkbutton(parent, text="Activer cette couleur",
                            variable=var_active,
                            command=toggle_active).grid(
                row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))
        else:
            ttk.Label(parent, text="Couleur principale (toujours active)").grid(
                row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))
            slot.active = True

        # Aperçu + boutons
        cnv = tk.Canvas(parent, width=64, height=36, bd=1, relief="solid",
                        highlightthickness=0)
        cnv.grid(row=1, column=0, rowspan=2, padx=(0, 10))
        # stocker la référence pour mise à jour
        slot._cnv = cnv

        ttk.Button(parent, text="Choisir couleur…",
                   command=lambda i=index: self._pick_via_dialog(i)).grid(
            row=1, column=1, sticky="ew", pady=2)
        ttk.Button(parent, text="Pipette écran",
                   command=lambda i=index: self._pick_via_eyedropper(i)).grid(
            row=2, column=1, sticky="ew", pady=2)

        # Tolérances
        ttk.Separator(parent, orient="horizontal").grid(
            row=3, column=0, columnspan=3, sticky="ew", pady=(6, 4))

        ttk.Label(parent, text="Tolerance teinte :").grid(row=4, column=0, sticky="w")
        lbl_h = ttk.Label(parent, text="15", width=3)
        ttk.Scale(parent, variable=slot.var_tol_h, from_=1, to=89,
                  orient="horizontal", length=180,
                  command=lambda v, lbl=lbl_h: lbl.config(
                      text=str(int(float(v))))).grid(row=4, column=1, sticky="w")
        lbl_h.grid(row=4, column=2, padx=(4, 0))

        ttk.Label(parent, text="Tolerance sat/val :").grid(row=5, column=0, sticky="w", pady=2)
        lbl_sv = ttk.Label(parent, text="60", width=3)
        ttk.Scale(parent, variable=slot.var_tol_sv, from_=1, to=130,
                  orient="horizontal", length=180,
                  command=lambda v, lbl=lbl_sv: lbl.config(
                      text=str(int(float(v))))).grid(row=5, column=1, sticky="w")
        lbl_sv.grid(row=5, column=2, padx=(4, 0))

    # ── Thème ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._current_theme = "dark" if self.var_dark_mode.get() else "light"
        t = THEMES[self._current_theme]
        try:
            self.tk.call("source", "")
        except Exception:
            pass
        # Application basique via option_add
        self.configure(bg=t["bg"])
        self.option_add("*Background",  t["bg"])
        self.option_add("*Foreground",  t["fg"])
        self.option_add("*Entry.Background", t["entry_bg"])
        self.option_add("*Entry.Foreground", t["fg"])
        # Forcer le rafraîchissement de tous les widgets
        self._apply_theme_recursive(self, t)

    def _apply_theme_recursive(self, widget, t: dict):
        cls = widget.winfo_class()
        try:
            if cls in ("Frame", "Labelframe", "TFrame", "TLabelframe"):
                widget.configure(bg=t["bg"])
            elif cls in ("Label", "TLabel"):
                widget.configure(bg=t["bg"], fg=t["fg"])
            elif cls in ("Canvas",):
                widget.configure(bg=t["bg"])
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._apply_theme_recursive(child, t)

    # ── Helpers internes ───────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        self.lbl_status.config(text=msg)

    def _refresh_timer_state(self):
        self.spn_timer.config(state="normal" if self.var_timer_on.get() else "disabled")

    def _refresh_jitter_state(self):
        self.spn_jitter.config(state="normal" if self.var_opt_jitter.get() else "disabled")

    def _refresh_startdelay_state(self):
        self.spn_start_delay.config(state="normal" if self.var_opt_start_d.get() else "disabled")

    def _refresh_all_color_previews(self):
        for slot in self._slots:
            if hasattr(slot, "_cnv"):
                r, g, b = slot.rgb
                slot._cnv.config(bg=f"#{r:02x}{g:02x}{b:02x}")

    def _refresh_zone_label(self):
        with zone_lock:
            z = ZONE
        self.lbl_zone.config(
            text=f"G={z['left']}  H={z['top']}  {z['width']} x {z['height']} px")

    # ── Sélection de couleur ───────────────────────────────────────────────────

    def _pick_via_dialog(self, index: int = 0):
        slot   = self._slots[index]
        result = colorchooser.askcolor(color=slot.rgb, title="Choisir la couleur cible")
        if result and result[0]:
            slot.rgb = tuple(int(c) for c in result[0])
            slot.hsv = rgb_to_hsv_cv(*slot.rgb)
            self._refresh_all_color_previews()
            self._set_status(f"Couleur {index+1} → RGB{slot.rgb}  HSV{slot.hsv}")

    def _pick_via_eyedropper(self, index: int = 0):
        self._eyedropper_target = index
        self.withdraw()
        self.after(250, self._show_eyedropper_overlay)

    def _show_eyedropper_overlay(self):
        overlay = tk.Toplevel(self)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.01)
        overlay.attributes("-topmost", True)
        overlay.config(cursor="crosshair")

        info = tk.Label(overlay,
                        text="Cliquez sur la couleur que vous souhaitez cibler",
                        font=("Segoe UI", 16, "bold"),
                        bg="#ffe066", fg="#1a1a1a", padx=12, pady=8)
        info.place(relx=0.5, rely=0.04, anchor="center")

        def on_click(event):
            sx, sy = event.x_root, event.y_root
            overlay.destroy()
            self.after(100, lambda: self._sample_pixel(sx, sy))

        overlay.bind("<Button-1>", on_click)
        overlay.focus_force()

    def _sample_pixel(self, sx: int, sy: int):
        with mss.mss() as sct:
            shot = sct.grab({"left": sx, "top": sy, "width": 1, "height": 1})
            arr  = np.frombuffer(shot.rgb, dtype=np.uint8)
            r, g, b = int(arr[0]), int(arr[1]), int(arr[2])
        index     = getattr(self, "_eyedropper_target", 0)
        slot      = self._slots[index]
        slot.rgb  = (r, g, b)
        slot.hsv  = rgb_to_hsv_cv(r, g, b)
        self._refresh_all_color_previews()
        self._set_status(f"Couleur {index+1} échantillonnée → RGB{slot.rgb}  HSV{slot.hsv}")
        self.deiconify()

    # ── Sélection de zone ──────────────────────────────────────────────────────

    def _pick_zone(self):
        self.withdraw()
        self.after(250, self._show_zone_overlay)

    def _show_zone_overlay(self):
        overlay = tk.Toplevel(self)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.35)
        overlay.attributes("-topmost", True)
        overlay.config(bg="black", cursor="cross")

        canvas = tk.Canvas(overlay, bg="black", highlightthickness=0, cursor="cross")
        canvas.pack(fill="both", expand=True)

        info = tk.Label(overlay,
                        text="Maintenez le clic gauche et glissez pour définir la zone",
                        font=("Segoe UI", 14, "bold"),
                        bg="#ffe066", fg="#1a1a1a", padx=10, pady=6)
        info.place(relx=0.5, rely=0.03, anchor="center")

        state = {"rect": None, "x0": 0, "y0": 0}

        def on_press(e):
            state["x0"], state["y0"] = e.x, e.y
            state["rect"] = canvas.create_rectangle(
                e.x, e.y, e.x, e.y, outline="#00ff00", width=2, dash=(6, 3))

        def on_drag(e):
            if state["rect"]:
                canvas.coords(state["rect"], state["x0"], state["y0"], e.x, e.y)

        def on_release(e):
            global ZONE
            x0 = min(state["x0"], e.x);  y0 = min(state["y0"], e.y)
            x1 = max(state["x0"], e.x);  y1 = max(state["y0"], e.y)
            w  = max(1, x1 - x0);        h  = max(1, y1 - y0)
            overlay.destroy()
            with zone_lock:
                ZONE = {"left": x0, "top": y0, "width": w, "height": h}
            self._refresh_zone_label()
            self.deiconify()

        canvas.bind("<ButtonPress-1>",   on_press)
        canvas.bind("<B1-Motion>",       on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        overlay.focus_force()

    def _reset_zone(self):
        global ZONE
        with zone_lock:
            ZONE = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        self._refresh_zone_label()
        self._set_status("Zone réinitialisée — plein écran.")

    # ── Raccourci clavier global ────────────────────────────────────────────────

    def _start_hotkey_listener(self):
        pressed = set()

        def on_press(key):
            try:
                pressed.add(key)
                shift = kb.Key.shift in pressed or kb.Key.shift_r in pressed
                ctrl  = kb.Key.ctrl_l in pressed or kb.Key.ctrl_r in pressed
                s     = kb.KeyCode.from_char('s') in pressed
                if ctrl and shift and s:
                    self.after(0, self._toggle)
            except Exception:
                pass

        def on_release(key):
            pressed.discard(key)

        threading.Thread(
            target=lambda: kb.Listener(on_press=on_press, on_release=on_release).run(),
            daemon=True).start()

    # ── Démarrage / arrêt ──────────────────────────────────────────────────────

    def _toggle(self):
        global running
        if not running:
            running = True
            self.btn_toggle.config(text="⏹  Arrêter")
            self._set_status("En cours…  (souris en haut-gauche = arrêt d'urgence)")
            threading.Thread(target=clicker_loop, args=(self,), daemon=True).start()
        else:
            running = False
            self.btn_toggle.config(text="▶  Démarrer", state="disabled")
            self._set_status("Arrêt demandé…")


# ── Point d'entrée ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    App().mainloop()
