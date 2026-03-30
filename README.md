# 🎯 Smart AutoClicker — by Colors

> Autoclicker intelligent qui détecte et clique automatiquement sur une couleur ciblée dans une zone définie de l'écran.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🎨 **Sélection de couleur** | Sélecteur classique ou pipette écran (1 clic sur n'importe quelle couleur) |
| 📐 **Zone de détection** | Dessinez un rectangle sur l'écran pour limiter la zone analysée |
| ⚡ **Clics / minute** | Réglez la cadence de 1 à 6000 CPM (défaut : 120 — naturel) |
| 🎲 **Taux d'erreur** | Simule des ratés humains (défaut : 5 %) pour un comportement crédible |
| ⏱️ **Timer** | Arrêt automatique après X secondes (optionnel) |
| 🔁 **Cooldown par cible** | Empêche de recliquer la même zone avant qu'elle disparaisse |
| ⌨️ **Raccourci clavier** | `Ctrl+Shift+S` pour démarrer/arrêter depuis n'importe quelle fenêtre |

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

5. **Démarrer**
   - Bouton `▶ Démarrer` dans l'interface
   - ou `Ctrl+Shift+S` depuis n'importe quelle fenêtre

> ⚠️ **Arrêt d'urgence** : déplacez la souris dans le coin haut-gauche de l'écran pour stopper immédiatement.

---

## 🗺️ Roadmap

### 🎨 Interface
- [ ] **Dark mode** — thème sombre optionnel
- [ ] **Overlay de prévisualisation** — afficher en temps réel les contours des cibles détectées (rectangle vert)
- [ ] **Historique des sessions** — tableau récapitulatif : clics, CPM moyen, durée, taux de réussite
- [ ] **Profils sauvegardables** — sauvegarder/charger un ensemble couleur + zone + paramètres dans un fichier JSON

### 🎯 Détection
- [ ] **Multi-couleurs** — détecter et cliquer sur plusieurs couleurs en parallèle
- [ ] **Priorité de clic** — choisir l'ordre : cible la plus proche du curseur, la plus grande, ou la plus haute
- [ ] **Filtre de forme** — exclure les formes non rondes (rectangles, lignes...)

### 🤖 Comportement naturel
- [ ] **Variation de cadence** — CPM flottant (ex : 120 ±20%) pour éviter des intervalles trop réguliers
- [ ] **Micro-déplacement aléatoire** — déplacer légèrement le curseur autour de la cible avant de cliquer
- [ ] **Délai de démarrage** — countdown configurable avant l'activation (laisser le temps de basculer dans le jeu)
- [ ] **Pause aléatoire** — insérer de courtes pauses spontanées pour simuler une distraction

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
