# 🔥 ARENA COMBAT - Battle Royale! 🔥

Un jeu de combat d'arène épique avec des balles de différents éléments qui s'affrontent dans des arènes géométriques dynamiques.

## 🎮 Fonctionnalités

### 🚀 Nouvelles améliorations
- **Menu de démarrage** avec configuration complète
- **Choix du nombre de balles** (3-25)
- **Durée personnalisable** (30-300 secondes)
- **Contrôle des perturbations** (5-30 secondes d'intervalle)
- **Fréquence des bonus ajustable** (3-20 secondes)
- **Sélection de la forme d'arène** (Hexagone, Octogone, Diamant)
- **Menu de fin** avec statistiques détaillées
- **Système de pause** (touche P)
- **Collision améliorée** - plus de balles qui traversent les murs!

### ⚔️ Types de Combattants
- **🔥 FEU** - Chasse activement les balles de glace
- **❄️ GLACE** - Ralentit progressivement 
- **⚙️ MÉTAL** - Attraction magnétique mutuelle
- **⚡ FOUDRE** - Mouvement erratique et imprévisible
- **☠️ POISON** - Empoisonne les balles proches

### 💎 Bonus Épiques
- **💨 VITESSE** - Accélération +50% pendant 5s
- **💚 SOIN** - Restaure 50 points de vie
- **🛡️ BOUCLIER** - Protection pendant 8s
- **✖️ CLONAGE** - Duplique la balle
- **😡 RAGE** - Triple les dégâts pendant 10s
- **❄️ FREEZE** - Gèle toutes les balles autour

### 🌀 Perturbations Dynamiques
- **🌀 GRAVITÉ INVERSÉE** - Force vers le haut
- **🧲 CHAMP MAGNÉTIQUE** - Attraction vers le centre
- **⚡ ACCÉLÉRATION** - Boost de vitesse global
- **💥 CHAOS TOTAL** - Mouvements aléatoires
- **🔄 MORPHING ARÈNE** - Change la forme de l'arène

## 🎯 Contrôles

### Menu
- **↑↓** - Naviguer dans les options
- **←→** - Ajuster les valeurs 
- **ENTRÉE/ESPACE** - Sélectionner
- **ESC** - Quitter

### Jeu
- **P** - Pause/Reprendre
- **ESC** - Retour au menu

## 🏆 Objectif

Survivez le plus longtemps possible dans l'arène! Les balles s'affrontent selon un système rock-paper-scissors étendu avec des multiplicateurs de dégâts. La dernière balle (ou type) debout gagne!

## 📊 Système de Combat

### Multiplicateurs de Dégâts
- **FEU** bat GLACE (x2.5) et POISON (x1.8)
- **GLACE** bat MÉTAL (x2.5) et FOUDRE (x1.8)  
- **MÉTAL** bat FOUDRE (x2.5) et POISON (x1.8)
- **FOUDRE** bat POISON (x2.5) et FEU (x1.2)
- **POISON** bat FEU (x2.5) et GLACE (x1.2)

## 🛠️ Installation

```bash
# Installer pygame
sudo apt install python3-pygame

# Ou avec pip (dans un environnement virtuel)
pip install pygame

# Lancer le jeu
python3 Main.py
```

## 🎨 Caractéristiques Techniques

- **Résolution**: 1080x1920 (format portrait)
- **FPS**: 60
- **Moteur**: Pygame 2.6+
- **Physique**: Collision géométrique avancée
- **Effets**: Particules, lueurs, animations fluides

## 🔧 Configuration Avancée

Toutes les configurations sont accessibles via le menu:
- Nombre de combattants initial
- Durée de la bataille  
- Fréquence des événements spéciaux
- Forme et style de l'arène

## 🏅 Statistiques de Fin

À la fin de chaque partie, consultez:
- Nombre de survivants
- Type dominant
- Bonus collectés
- Perturbations déclenchées
- Durée totale de la bataille

---

**Développé avec passion pour une expérience de jeu intense et spectaculaire!** 🚀