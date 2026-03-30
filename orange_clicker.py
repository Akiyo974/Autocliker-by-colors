"""
Smart AutoClicker
-----------------
Détecte et clique automatiquement sur des zones d'une couleur choisie.

Dépendances :
    pip install opencv-python mss pyautogui numpy pynput

Utilisation :
    1. Lancez le script — une interface graphique s'ouvre.
    2. Choisissez la couleur cible :
         • "Choisir couleur…"  → sélecteur de couleur classique
         • "Pipette écran"     → cliquez n'importe où sur l'écran pour échantillonner
    3. Ajustez les tolérances jusqu'à ce que la détection soit bonne.
    4. Dessinez la zone où chercher (optionnel — plein écran par défaut).
    5. Cliquez sur "Démarrer".
    6. Ctrl+Shift+S  → démarrer / arrêter depuis n'importe quelle fenêtre.
    7. Souris en haut-gauche = arrêt d'urgence (failsafe PyAutoGUI).
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
    """Retourne (low, high) numpy uint8 pour cv2.inRange, avec gestion du rouge (H wrapping)."""
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

# ── Boucle de clic ─────────────────────────────────────────────────────────────

def clicker_loop(app: "App"):
    global running
    pyautogui.PAUSE    = 0
    pyautogui.FAILSAFE = True

    clicked_total = 0
    t_start       = time.perf_counter()
    last_click_t  = 0.0  # timestamp du dernier clic
    use_timer     = app.get_timer_enabled()
    timer_end     = t_start + app.get_timer_seconds() if use_timer else None
    # cooldown par position : {(cx,cy): timestamp_dernier_clic}
    pos_cooldown: dict = {}
    COOLDOWN_RADIUS = 20  # pixels — deux centres < 20px = même cible

    def is_on_cooldown(cx, cy, cooldown_s):
        now = time.perf_counter()
        for (px, py), t in list(pos_cooldown.items()):
            if abs(cx - px) < COOLDOWN_RADIUS and abs(cy - py) < COOLDOWN_RADIUS:
                if now - t < cooldown_s:
                    return True
                else:
                    del pos_cooldown[(px, py)]
        return False

    with mss.mss() as sct:
        while running:
            with zone_lock:
                region = dict(ZONE)

            # Arrêt automatique si le timer est actif
            if timer_end is not None:
                remaining = timer_end - time.perf_counter()
                if remaining <= 0:
                    running = False
                    break
                app.after(0, lambda r=remaining: app._set_status(
                    f"En cours…  ⏱ {int(r)}s restantes"))
            h, s, v   = app.get_hsv()
            tol_h     = app.get_tol_h()
            tol_sv    = app.get_tol_sv()
            low, high = build_hsv_range(h, s, v, tol_h, tol_sv)
            min_r     = app.get_min_radius()
            cpm       = max(1, app.get_cpm())
            interval  = 60.0 / cpm  # secondes entre deux clics
            miss_rate = app.get_miss_rate()
            cooldown_s = app.get_cooldown()

            raw       = sct.grab(region)
            frame_rgb = np.frombuffer(raw.rgb, dtype=np.uint8).reshape(raw.height, raw.width, 3)
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            centers = detect_targets(frame_bgr, low, high, min_r)

            for (cx, cy) in centers:
                if not running:
                    break
                # Ignorer si cette position est encore en cooldown
                if cooldown_s > 0 and is_on_cooldown(cx, cy, cooldown_s):
                    continue
                # Attendre si le délai entre clics n'est pas écoulé
                wait = interval - (time.perf_counter() - last_click_t)
                if wait > 0:
                    time.sleep(wait)
                if not running:
                    break
                # Simuler un raté humain
                if random.random() < miss_rate:
                    last_click_t = time.perf_counter()
                    pos_cooldown[(cx, cy)] = last_click_t
                    continue
                pyautogui.click(region["left"] + cx, region["top"] + cy)
                last_click_t = time.perf_counter()
                pos_cooldown[(cx, cy)] = last_click_t
                clicked_total += 1

    elapsed = time.perf_counter() - t_start
    cps     = clicked_total / elapsed if elapsed > 0 else 0
    app.after(0, lambda: app.on_clicker_stopped(clicked_total, cps))

# ── Interface graphique ────────────────────────────────────────────────────────

class App(tk.Tk):
    _PAD = 10

    def __init__(self):
        super().__init__()
        self.title("Smart AutoClicker")
        self.resizable(False, False)

        # Couleur par défaut : orange
        self._rgb = (255, 140, 0)
        self._hsv = rgb_to_hsv_cv(*self._rgb)

        self._build_ui()
        self._refresh_color_preview()
        self._refresh_zone_label()
        self._start_hotkey_listener()

    # ── Getters thread-safe pour clicker_loop ──────────────────────────────────

    def get_hsv(self):        return self._hsv
    def get_tol_h(self):      return self.var_tol_h.get()
    def get_tol_sv(self):     return self.var_tol_sv.get()
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

    # ── Callback fin de session ────────────────────────────────────────────────

    def on_clicker_stopped(self, total: int, cps: float):
        global running
        running = False
        self.btn_toggle.config(text="▶  Démarrer", state="normal")
        self._set_status(f"Arrêté — {total} clics  ({cps:.1f} clics/s)")

    # ── Construction de l'UI ───────────────────────────────────────────────────

    def _build_ui(self):
        P = self._PAD

        # ── Section couleur ────────────────────────────────────────────────────
        frm_col = ttk.LabelFrame(self, text=" Couleur cible ", padding=P)
        frm_col.grid(row=0, column=0, padx=P, pady=(P, 4), sticky="ew")

        # Aperçu couleur
        self.cnv_color = tk.Canvas(frm_col, width=64, height=36, bd=1, relief="solid",
                                   highlightthickness=0)
        self.cnv_color.grid(row=0, column=0, rowspan=2, padx=(0, 10))

        ttk.Button(frm_col, text="Choisir couleur…",
                   command=self._pick_via_dialog).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(frm_col, text="Pipette ecran  (cliquer sur l'ecran)",
                   command=self._pick_via_eyedropper).grid(row=1, column=1, sticky="ew", pady=2)

        # Tolérances
        ttk.Separator(frm_col, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(8, 4))

        ttk.Label(frm_col, text="Tolerance teinte :").grid(row=3, column=0, sticky="w")
        self.var_tol_h  = tk.IntVar(value=15)
        self.lbl_tol_h  = ttk.Label(frm_col, text="15", width=3)
        ttk.Scale(frm_col, variable=self.var_tol_h, from_=1, to=89,
                  orient="horizontal", length=200,
                  command=lambda v: self.lbl_tol_h.config(
                      text=str(int(float(v))))).grid(row=3, column=1, sticky="w")
        self.lbl_tol_h.grid(row=3, column=2, padx=(4, 0))

        ttk.Label(frm_col, text="Tolerance sat/val :").grid(row=4, column=0, sticky="w", pady=2)
        self.var_tol_sv = tk.IntVar(value=60)
        self.lbl_tol_sv = ttk.Label(frm_col, text="60", width=3)
        ttk.Scale(frm_col, variable=self.var_tol_sv, from_=1, to=130,
                  orient="horizontal", length=200,
                  command=lambda v: self.lbl_tol_sv.config(
                      text=str(int(float(v))))).grid(row=4, column=1, sticky="w")
        self.lbl_tol_sv.grid(row=4, column=2, padx=(4, 0))

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
        self.var_cpm = tk.IntVar(value=120)  # 120 CPM ≈ naturel
        self.lbl_cpm = ttk.Label(frm_par, text="120", width=5)
        ttk.Scale(frm_par, variable=self.var_cpm, from_=1, to=6000,
                  orient="horizontal", length=200,
                  command=lambda v: self.lbl_cpm.config(
                      text=str(int(float(v))))).grid(row=1, column=1, sticky="w", pady=(4, 0))
        self.lbl_cpm.grid(row=1, column=2, padx=(4, 0))

        ttk.Label(frm_par, text="Taux d'erreur (%) :").grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.var_miss = tk.IntVar(value=5)  # 5 % de clics ratés par défaut
        self.lbl_miss = ttk.Label(frm_par, text="5 %", width=5)
        ttk.Scale(frm_par, variable=self.var_miss, from_=0, to=80,
                  orient="horizontal", length=200,
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

        # ── Contrôles ──────────────────────────────────────────────────────────
        frm_ctrl = ttk.Frame(self)
        frm_ctrl.grid(row=3, column=0, padx=P, pady=P, sticky="ew")
        frm_ctrl.columnconfigure(0, weight=1)

        self.btn_toggle = ttk.Button(frm_ctrl, text="▶  Démarrer",
                                     command=self._toggle)
        self.btn_toggle.grid(row=0, column=0, sticky="ew")

        # ── Statut ─────────────────────────────────────────────────────────────
        self.lbl_status = ttk.Label(self, text="Prêt.  |  Raccourci : Ctrl+Shift+S",
                                    anchor="w", relief="sunken", padding=(4, 2))
        self.lbl_status.grid(row=4, column=0, padx=P, pady=(0, P), sticky="ew")

    # ── Helpers internes ───────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        self.lbl_status.config(text=msg)

    def _refresh_timer_state(self):
        self.spn_timer.config(state="normal" if self.var_timer_on.get() else "disabled")

    def _refresh_color_preview(self):
        r, g, b = self._rgb
        self.cnv_color.config(bg=f"#{r:02x}{g:02x}{b:02x}")

    def _refresh_zone_label(self):
        with zone_lock:
            z = ZONE
        self.lbl_zone.config(
            text=f"G={z['left']}  H={z['top']}  {z['width']} x {z['height']} px")

    # ── Sélection de couleur ───────────────────────────────────────────────────

    def _pick_via_dialog(self):
        result = colorchooser.askcolor(color=self._rgb, title="Choisir la couleur cible")
        if result and result[0]:
            self._rgb = tuple(int(c) for c in result[0])
            self._hsv = rgb_to_hsv_cv(*self._rgb)
            self._refresh_color_preview()
            self._set_status(f"Couleur → RGB{self._rgb}  HSV{self._hsv}")

    def _pick_via_eyedropper(self):
        """Masque la fenêtre, affiche un overlay transparent, capture la couleur au clic."""
        self.withdraw()
        self.after(250, self._show_eyedropper_overlay)

    def _show_eyedropper_overlay(self):
        overlay = tk.Toplevel(self)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.01)      # quasi-invisible
        overlay.attributes("-topmost", True)
        overlay.config(cursor="crosshair")

        # Bandeau d'instruction visible
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
        self._rgb = (r, g, b)
        self._hsv = rgb_to_hsv_cv(r, g, b)
        self._refresh_color_preview()
        self._set_status(f"Couleur échantillonnée → RGB{self._rgb}  HSV{self._hsv}")
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
        """Démarre un listener global : Ctrl+Shift+S → démarrer/arrêter."""
        HOTKEY = {kb.Key.ctrl_l, kb.KeyCode.from_char('s')}
        HOTKEY_R = {kb.Key.ctrl_r, kb.KeyCode.from_char('s')}
        pressed = set()

        def on_press(key):
            try:
                pressed.add(key)
                # Ctrl (gauche ou droit) + Shift + S
                shift = kb.Key.shift in pressed or kb.Key.shift_r in pressed
                ctrl  = kb.Key.ctrl_l in pressed or kb.Key.ctrl_r in pressed
                s     = kb.KeyCode.from_char('s') in pressed
                if ctrl and shift and s:
                    self.after(0, self._toggle)
            except Exception:
                pass

        def on_release(key):
            pressed.discard(key)

        t = threading.Thread(
            target=lambda: kb.Listener(on_press=on_press, on_release=on_release).run(),
            daemon=True)
        t.start()

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
