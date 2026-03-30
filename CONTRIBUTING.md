# 🤝 Contribuer à Smart AutoClicker

Merci de l'intérêt que vous portez à ce projet ! Toute contribution est la bienvenue.

---

## 📋 Types de contributions

| Type | Comment |
|---|---|
| 🐛 Bug | Ouvrir une [Issue bug](https://github.com/Akiyo974/Autocliker-by-colors/issues/new?template=bug_report.yml) |
| 💡 Feature | Ouvrir une [Issue feature](https://github.com/Akiyo974/Autocliker-by-colors/issues/new?template=feature_request.yml) |
| 🔧 Code | Forker → brancher → PR |
| 📝 Docs | Même flow que le code |

---

## 🛠️ Environnement de développement

```bash
# 1. Forker le dépôt sur GitHub, puis :
git clone https://github.com/<votre-pseudo>/Autocliker-by-colors.git
cd Autocliker-by-colors

# 2. Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## 🔀 Workflow Git

```bash
# Créer une branche descriptive
git checkout -b feat/multi-screen-support
git checkout -b fix/cooldown-edge-case
git checkout -b docs/improve-cli-examples

# Commiter avec des messages conventionnels (voir ci-dessous)
git commit -m "feat: ajouter le support multi-écrans"

# Pousser et ouvrir une PR
git push origin feat/multi-screen-support
```

---

## 📝 Convention de commits

Ce projet suit les [Conventional Commits](https://www.conventionalcommits.org/) :

| Préfixe | Usage |
|---|---|
| `feat:` | Nouvelle fonctionnalité |
| `fix:` | Correction de bug |
| `docs:` | Documentation uniquement |
| `refactor:` | Refactoring sans ajout de feature ni fix |
| `style:` | Formatage, espaces, virgules (pas de logique) |
| `perf:` | Amélioration de performance |
| `test:` | Ajout ou modification de tests |
| `chore:` | Maintenance, dépendances, CI |

---

## ✅ Checklist avant une PR

- [ ] Le code respecte la **PEP 8** (longueur de ligne ≤ 100 caractères)
- [ ] Les commentaires sont en **français** (cohérence avec le codebase)
- [ ] J'ai testé manuellement la modification (GUI et/ou CLI selon le cas)
- [ ] Le **README** est mis à jour si nécessaire
- [ ] Le **CHANGELOG** est mis à jour (section `[Unreleased]`)
- [ ] Aucun fichier inutile n'est inclus (`.venv/`, `__pycache__/`, etc.)

---

## 🎨 Style de code

- **Indentation** : 4 espaces
- **Guillemets** : doubles `"`
- **Variables** : `snake_case`
- **Classes** : `PascalCase`
- **Constantes** : `UPPER_SNAKE_CASE`
- **Imports** : stdlib → tiers (séparés par une ligne vide)

---

## 💬 Questions ?

Ouvrez une discussion sur [GitHub Discussions](https://github.com/Akiyo974/Autocliker-by-colors/discussions) plutôt qu'une Issue pour les questions générales.
