<div align="center">

# 🎯 Smart AutoClicker — by Colors

**Détecte et clique automatiquement sur des couleurs ciblées.**  
Interface graphique complète **ou** pilotage en ligne de commande, avec des options de naturalisation pour un comportement humain crédible.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Akiyo974/Autocliker-by-colors?color=f59e0b)](https://github.com/Akiyo974/Autocliker-by-colors/commits/main)
[![Issues](https://img.shields.io/github/issues/Akiyo974/Autocliker-by-colors)](https://github.com/Akiyo974/Autocliker-by-colors/issues)
[![Stars](https://img.shields.io/github/stars/Akiyo974/Autocliker-by-colors?style=social)](https://github.com/Akiyo974/Autocliker-by-colors/stargazers)

</div>

---

## ✨ Fonctionnalités

| | Fonctionnalité | Description |
|---|---|---|
| 🎨 | **Multi-couleurs** | Jusqu'à 3 couleurs simultanées, chacune avec sa propre tolérance HSV |
| 🖱️ | **Sélection de couleur** | Roue chromatique ou pipette écran (1 clic n'importe où) |
| 📐 | **Zone de détection** | Dessinez un rectangle sur l'écran pour limiter la zone analysée |
| ⚡ | **Clics / minute** | Cadence de 1 à 6000 CPM — défaut 120 (naturel humain) |
| 🎲 | **Taux d'erreur** | Simule des ratés humains — défaut 5 % |
| ⏱️ | **Timer** | Arrêt automatique après N secondes |
| 🔁 | **Cooldown par cible** | Empêche de recliquer la même zone avant qu'elle disparaisse |
| ⌨️ | **Raccourci global** | `Ctrl+Shift+S` pour démarrer/arrêter depuis n'importe quelle fenêtre |
| 🌙 | **Dark mode** | Thème sombre activable en un clic |
| 👁️ | **Overlay preview** | Fenêtre OpenCV cerclant les cibles détectées en vert (temps réel) |
| 📊 | **Variation de cadence** | CPM ±20 % aléatoire pour casser la régularité |
| 🎯 | **Micro-déplacement** | Décalage aléatoire ±N px autour du centre de la cible |
| ⏳ | **Délai de démarrage** | Compte à rebours configurable avant le premier clic |
| ☕ | **Pauses aléatoires** | Pauses spontanées 0.3–1.5 s toutes les 8–20 clics |
| 💻 | **Mode CLI** | Pilotage complet sans interface graphique |

---

## 🚀 Démarrage rapide

### Prérequis
- Python **3.10+**
- Windows (capture écran via Win32)

### Installation

```bash
git clone https://github.com/Akiyo974/Autocliker-by-colors.git
cd Autocliker-by-colors
pip install -r requirements.txt
```

### Lancer

```bash
# Mode GUI (interface graphique)
python orange_clicker.py

# Mode CLI (sans interface)
python orange_clicker.py --cli --color FF8C00 --cpm 150
```

---

## 🖥️ Mode GUI

1. **Choisir la couleur cible** (onglets Couleur 1 / 2 / 3)
   - `Choisir couleur…` → roue chromatique
   - `Pipette écran` → cliquez directement sur la couleur dans votre application

2. **Ajuster les tolérances**
   - *Tolérance teinte* — élargit la plage de teinte acceptée
   - *Tolérance sat/val* — gère les variations de luminosité/saturation

3. **Définir la zone** *(optionnel — plein écran par défaut)*
   - `Dessiner la zone…` → glissez un rectangle sur l'écran

4. **Régler les paramètres**
   - CPM · Taux d'erreur · Cooldown cible · Timer

5. **Activer les options naturalisation**  
   *(section Options en bas)*

| Option | Effet |
|---|---|
| Dark mode | Thème sombre instantané |
| Overlay preview | Fenêtre OpenCV avec cibles cerclées |
| Variation de cadence | CPM ±20 % aléatoire |
| Micro-déplacement | Clic décalé de ±N px |
| Délai de démarrage | Compte à rebours avant activation |
| Pauses aléatoires | Pauses 0.3–1.5 s toutes les 8–20 clics |

6. **Démarrer** — bouton `▶ Démarrer` ou `Ctrl+Shift+S`

> ⚠️ **Arrêt d'urgence** : souris dans le coin haut-gauche = stop immédiat (failsafe PyAutoGUI).

---

## ⌨️ Mode CLI

### Syntaxe

```
python orange_clicker.py --cli [OPTIONS]
```

### Démonstration

```
╔══════════════════════════════════════════════════╗
║  Smart AutoClicker  —  CLI mode                  ║
╠══════════════════════════════════════════════════╣
║  Couleurs    : #FF8C00, #00C850                  ║
║  Zone        : 0,0  1920x1080 px                 ║
║  CPM         : 200                               ║
║  Taux erreur : 5.0 %                             ║
║  Cooldown    : 300 ms                            ║
║  Timer       : 60 s                              ║
║  Options     : variation CPM, jitter ±5px        ║
╠══════════════════════════════════════════════════╣
║  Ctrl+C pour arrêter                             ║
╚══════════════════════════════════════════════════╝

[•] En cours…  ⏱ 58s restantes
```

### Options

| Option | Type | Défaut | Description |
|---|---|---|---|
| `--color RRGGBB[:tol_h[:tol_sv]]` | string | — | Couleur cible (hex). **Répétable jusqu'à 3×** |
| `--zone x,y,w,h` | int,int,int,int | plein écran | Zone de détection |
| `--cpm N` | int | 120 | Clics par minute |
| `--miss N` | float | 5.0 | Taux d'erreur en % |
| `--cooldown N` | int | 300 | Cooldown par cible en ms |
| `--radius N` | int | 8 | Rayon minimum de détection (px) |
| `--timer N` | int | 0 | Durée en secondes (0 = infini) |
| `--tol-h N` | int | 15 | Tolérance teinte par défaut |
| `--tol-sv N` | int | 60 | Tolérance sat/val par défaut |
| `--jitter N` | int | 0 | Micro-déplacement ±px (0 = off) |
| `--start-delay N` | int | 0 | Délai avant 1er clic (secondes) |
| `--cpm-variation` | flag | off | Variation cadence ±20 % |
| `--random-pauses` | flag | off | Pauses aléatoires spontanées |

### Exemples

```bash
# Orange, plein écran, 150 CPM
python orange_clicker.py --cli --color FF8C00 --cpm 150

# 2 couleurs avec tolérances custom, zone précise, timer 2 min
python orange_clicker.py --cli \
  --color FF8C00:20:80 \
  --color 00C850:15:60 \
  --zone 0,100,1920,800 \
  --cpm 200 --timer 120

# Mode furtif maximal
python orange_clicker.py --cli --color 3478FF \
  --cpm 90 --miss 8 --jitter 6 \
  --cpm-variation --random-pauses --start-delay 5
```

---

## 🗺️ Roadmap

### 🎨 Interface
- [x] **Dark mode** — thème sombre optionnel
- [x] **Overlay de prévisualisation** — cibles cerclées en vert en temps réel
- [ ] **Historique des sessions** — tableau récapitulatif (clics, CPM moyen, durée)
- [ ] **Profils sauvegardables** — exporter/importer les réglages en JSON

### 🎯 Détection
- [x] **Multi-couleurs** — jusqu'à 3 couleurs en parallèle
- [ ] **Priorité de clic** — cible la plus proche / la plus grande / la plus haute
- [ ] **Filtre de forme** — exclure les formes non rondes

### 🤖 Comportement naturel
- [x] **Variation de cadence** — CPM ±20 % aléatoire
- [x] **Micro-déplacement aléatoire** — décalage ±N px avant le clic
- [x] **Délai de démarrage** — countdown configurable
- [x] **Pauses aléatoires** — pauses spontanées entre les clics

### 🛠️ Technique
- [x] **Mode CLI** — pilotage complet sans interface graphique
- [ ] **Packaging `.exe`** — exécutable standalone via PyInstaller
- [ ] **Support multi-écrans** — choisir le moniteur cible

---

## 📁 Structure du projet

```
Autocliker-by-colors/
├── orange_clicker.py   # Script principal (GUI + CLI)
├── requirements.txt    # Dépendances Python
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.yml
    │   ├── feature_request.yml
    │   └── config.yml
    └── PULL_REQUEST_TEMPLATE.md
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les instructions.

- 🐛 [Signaler un bug](https://github.com/Akiyo974/Autocliker-by-colors/issues/new?template=bug_report.yml)
- 💡 [Proposer une fonctionnalité](https://github.com/Akiyo974/Autocliker-by-colors/issues/new?template=feature_request.yml)
- 🔧 [Ouvrir une Pull Request](https://github.com/Akiyo974/Autocliker-by-colors/compare)

---

## ⚙️ Dépendances

| Package | Version | Rôle |
|---|---|---|
| `opencv-python` | ≥ 4.8 | Détection de couleur (HSV, contours) |
| `mss` | ≥ 9.0 | Capture d'écran ultra-rapide |
| `pyautogui` | ≥ 0.9 | Simulation de clics souris |
| `numpy` | ≥ 1.24 | Traitement des tableaux d'images |
| `pynput` | ≥ 1.7 | Écoute du raccourci clavier global |

---

## 📋 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique détaillé des versions.

---

## 📄 Licence

Ce projet est distribué sous licence [MIT](LICENSE).

---

<div align="center">

Fait avec ❤️ par **[Akiyo974](https://github.com/Akiyo974)**  
⭐ Une étoile si le projet vous est utile !

</div>


![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🎨 **Multi-couleurs** | Jusqu'à 3 couleurs simultanées, chacune avec sa propre tolérance |
| 🖱️ **Sélection de couleur** | Sélecteur classique ou pipette écran par onglet couleur |
| 📐 **Zone de détection** | Dessinez un rectangle sur l'écran pour limiter la zone analysée |
| ⚡ **Clics / minute** | Réglez la cadence de 1 à 6000 CPM (défaut : 120 — naturel) |
| 🎲 **Taux d'erreur** | Simule des ratés humains (défaut : 5 %) pour un comportement crédible |
| ⏱️ **Timer** | Arrêt automatique après X secondes (optionnel) |
| 🔁 **Cooldown par cible** | Empêche de recliquer la même zone avant qu'elle disparaisse |
| ⌨️ **Raccourci clavier** | `Ctrl+Shift+S` pour démarrer/arrêter depuis n'importe quelle fenêtre |
| 🌙 **Dark mode** | Thème sombre activable en un clic |
| 👁️ **Overlay preview** | Fenêtre OpenCV montrant les cibles détectées en temps réel (activable) |
| 📊 **Variation de cadence** | CPM légèrement aléatoire ±20 % (activable) |
| 🎯 **Micro-déplacement** | Décalage aléatoire du point de clic ±N px (activable) |
| ⏳ **Délai de démarrage** | Compte à rebours configurable avant le premier clic (activable) |
| ☕ **Pauses aléatoires** | Pauses spontanées entre les clics pour simuler une distraction (activable) |

---

## 📸 Aperçu

![Interface](https://i.imgur.com/placeholder.png)

---

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur
- Windows (utilise l'API Win32 pour la capture d'écran)

### 1. Cloner le dépôt

```bash
git clone https://github.com/Akiyo974/Autocliker-by-colors.git
cd Autocliker-by-colors
```

### 2. Installer les dépendances

```bash
pip install opencv-python mss pyautogui numpy pynput
```

### 3. Lancer

```bash
python orange_clicker.py
```

---

## 🛠️ Utilisation

1. **Choisir la couleur cible**
   - `Choisir couleur…` → roue chromatique
   - `Pipette écran` → cliquez directement sur la couleur dans votre application

2. **Ajuster les tolérances**
   - *Tolérance teinte* : élargit la plage de couleur acceptée
   - *Tolérance sat/val* : gère les variations de luminosité

3. **Définir la zone de détection** *(optionnel)*
   - `Dessiner la zone…` → délimitez la région à surveiller
   - `Plein écran` → aucune limite

4. **Paramètres**
   - **Clics / minute** : cadence (120 = naturel, 400+ = rapide)
   - **Taux d'erreur** : % de clics volontairement ratés (naturel ≥ 5 %)
   - **Cooldown cible** : délai avant de recliquer la même zone (évite les doublons)
   - **Timer** : arrêt automatique après N secondes

5. **Options** *(section dédiée, tout activable/désactivable)*
   - **Dark mode** — thème sombre
   - **Overlay prévisualisation** — fenêtre OpenCV avec les cibles encerclées en vert
   - **Variation de cadence** — CPM ±20 % aléatoire à chaque clic
   - **Micro-déplacement** — décalage ±N px autour de la cible
   - **Délai de démarrage** — compte à rebours avant activation
   - **Pauses aléatoires** — pauses 0.3–1.5 s toutes les 8–20 clics

6. **Démarrer**
   - Bouton `▶ Démarrer` dans l'interface
   - ou `Ctrl+Shift+S` depuis n'importe quelle fenêtre

> ⚠️ **Arrêt d'urgence** : déplacez la souris dans le coin haut-gauche de l'écran pour stopper immédiatement.

---

## 🗺️ Roadmap

### 🎨 Interface
- [x] **Dark mode** — thème sombre optionnel
- [x] **Overlay de prévisualisation** — afficher en temps réel les contours des cibles détectées (cercle vert)
- [ ] **Historique des sessions** — tableau récapitulatif : clics, CPM moyen, durée, taux de réussite
- [ ] **Profils sauvegardables** — sauvegarder/charger un ensemble couleur + zone + paramètres dans un fichier JSON

### 🎯 Détection
- [x] **Multi-couleurs** — détecter et cliquer sur plusieurs couleurs en parallèle (jusqu'à 3)
- [ ] **Priorité de clic** — choisir l'ordre : cible la plus proche du curseur, la plus grande, ou la plus haute
- [ ] **Filtre de forme** — exclure les formes non rondes (rectangles, lignes...)

### 🤖 Comportement naturel
- [x] **Variation de cadence** — CPM flottant (±20%) pour éviter des intervalles trop réguliers
- [x] **Micro-déplacement aléatoire** — déplacer légèrement le curseur autour de la cible avant de cliquer
- [x] **Délai de démarrage** — countdown configurable avant l'activation (laisser le temps de basculer dans le jeu)
- [x] **Pauses aléatoires** — insérer de courtes pauses spontanées pour simuler une distraction

### 🛠️ Technique
- [ ] **Packaging `.exe`** — distribuer un exécutable standalone via PyInstaller (sans Python requis)
- [ ] **Support multi-écrans** — choisir sur quel moniteur chercher les cibles
- [ ] **Mode CLI** — lancer sans interface graphique via arguments en ligne de commande

---

## ⚙️ Dépendances

| Package | Rôle |
|---|---|
| `opencv-python` | Détection de couleur par vision par ordinateur |
| `mss` | Capture d'écran ultra-rapide |
| `pyautogui` | Simulation de clics souris |
| `numpy` | Traitement des images |
| `pynput` | Écoute du raccourci clavier global |

---

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).

---

## 👤 Auteur

**Akiyo974**  
[GitHub](https://github.com/Akiyo974)
