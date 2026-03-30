# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
ce projet respecte le [Semantic Versioning](https://semver.org/lang/fr/).

---

## [Unreleased]

---

## [1.3.0] — 2026-03-30

### Ajouté
- **Mode CLI** complet via `--cli` : pilotage sans interface graphique avec affichage récapitulatif dans le terminal
- **Multi-couleurs** : jusqu'à 3 couleurs simultanées avec onglets dédiés (Couleur 1/2/3), chacun avec aperçu visuel, pipette et tolérances indépendantes
- **Dark mode** : thème sombre activable depuis la section Options
- **Overlay de prévisualisation** : fenêtre OpenCV affichant les cibles cerclées en vert en temps réel (activable)
- **Variation de cadence** : CPM ±20 % aléatoire pour briser la régularité (activable)
- **Micro-déplacement** : décalage aléatoire ±N px du point de clic (activable, valeur configurable)
- **Délai de démarrage** : compte à rebours en secondes avant le premier clic (activable)
- **Pauses aléatoires** : pauses de 0.3–1.5 s toutes les 8–20 clics (activable)
- `CONTRIBUTING.md` — guide de contribution
- `CHANGELOG.md` — historique des versions
- Templates GitHub : bug report, feature request, PR template, config issues

### Modifié
- Section couleur remplacée par un `Notebook` à 3 onglets
- README entièrement réécrit (badges, section CLI, table options, structure projet)
- Roadmap mise à jour : 8 items cochés sur 13

---

## [1.2.0] — 2026-03-28

### Ajouté
- **Cooldown par position** : évite de recliquer la même cible encore visible (`COOLDOWN_RADIUS = 20 px`)
- Champ UI « Cooldown cible (ms) » (défaut : 300 ms)
- Raccourci global **Ctrl+Shift+S** via `pynput` pour démarrer/arrêter depuis n'importe quelle fenêtre
- **Slider CPM** (1–6000, défaut : 120) — rythme de clic configurable
- **Slider taux d'erreur** (0–80 %, défaut : 5 %) — simule des ratés humains
- **Timer optionnel** : checkbox + spinbox, affichage du compte à rebours dans la barre de statut

### Corrigé
- Bug : 181 clics envoyés mais seulement ~90 enregistrés (cibles re-détectées sur chaque frame → doublons ignorés par le jeu)

---

## [1.1.0] — 2026-03-27

### Ajouté
- Interface graphique complète (`tkinter` + `ttk`)
- Sélecteur de couleur via roue chromatique (`colorchooser`)
- **Pipette écran** : overlay fullscreen quasi-invisible + curseur crosshair + échantillonnage pixel
- **Dessin de zone** : overlay semi-transparent, glisser-déposer rectangle vert
- Tolérances HSV : sliders *tolérance teinte* (1–89) et *tolérance sat/val* (1–130)
- Aperçu couleur (canvas coloré mis à jour en temps réel)
- Affichage zone active dans l'UI
- Barre de statut (prêt, en cours, arrêté + stats)
- Bouton Démarrer/Arrêter avec désactivation pendant l'arrêt
- Détection multi-contours via `cv2.findContours`

### Modifié
- Remplacement du script terminal orange-only par une application GUI complète
- Pipeline de détection : RGB → BGR → HSV → `inRange` → morphologie → contours → centres

---

## [1.0.0] — 2026-03-26

### Ajouté
- Détection initiale de la couleur orange uniquement
- Capture d'écran via `mss`
- Simulation de clics via `pyautogui`
- Script terminal basique (sans GUI)

[Unreleased]: https://github.com/Akiyo974/Autocliker-by-colors/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/Akiyo974/Autocliker-by-colors/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Akiyo974/Autocliker-by-colors/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Akiyo974/Autocliker-by-colors/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Akiyo974/Autocliker-by-colors/releases/tag/v1.0.0
