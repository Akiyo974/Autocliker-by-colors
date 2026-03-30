# 🎯 Smart AutoClicker — by Colors

> Autoclicker intelligent qui détecte et clique automatiquement sur 1 à 3 couleurs ciblées dans une zone définie de l'écran, avec un ensemble d'options de naturalisation activables.

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
