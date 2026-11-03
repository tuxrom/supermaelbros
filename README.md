# Super Maël Bros

Jeu de plateforme 2D, contenu dans un seul fichier : `index.html` (canvas + JavaScript, aucune dépendance).
Ouvre-le dans un navigateur, sur ordinateur ou sur mobile.

- 4 mondes de 3 niveaux : Prairies de l'Aube, Grottes Chantantes, Bois de Lune, Citadelle de Ferroc (boss).
- Clavier : flèches ou WASD, Espace pour sauter, Maj pour courir, Échap ou P pour la pause, M pour couper la musique, F pour le plein écran. Manette standard reconnue.
- Mobile : croix directionnelle, boutons A (saut) et B (course), multi-touch, mode paysage.
- Progression sauvegardée dans le `localStorage` du navigateur.

Les niveaux sont des tableaux de tuiles assemblés par `tools/levelgen.py`, qui les réinjecte dans `index.html` :

```
python3 tools/levelgen.py
```
