# Projet de Traitement d'Images : Tatouage Numérique

**Réalisé par** : Dhia Roueg & Mohamed Amine Gharbi  
**Classe** : GI1-S1

## 📌 Introduction

Le **tatouage numérique** (ou *watermarking*) est une technique de dissimulation d’informations (texte, image, signature…) dans un fichier multimédia (image, audio, vidéo), à des fins de :

- **Protection contre le piratage**
- **Vérification d’authenticité**
- **Traçabilité**

Ce projet explore différentes techniques de tatouage numérique appliquées aux **images**, en utilisant **Python** et des bibliothèques de traitement d’images. Une **interface graphique** a également été développée pour faciliter l'utilisation.

---

## 🧠 Fonctionnalités

- Tatouage par **LSB** (Least Significant Bit)
- Tatouage par **DCT** (Discrete Cosine Transform)
- Tatouage par **DWT** (Discrete Wavelet Transform)
- Extraction (décodage) pour chaque méthode
- **Interface graphique** conviviale avec PyQt5
- Prise en charge de watermark textuel ou image
- Sauvegarde automatique d'images tatouées

---

## 🛠️ Technologies et Librairies utilisées

- `Python 3`
- `OpenCV (cv2)`
- `NumPy`
- `Matplotlib`
- `Pillow (PIL)`
- `PyWavelets (pywt)`
- `PyQt5`

---

## 🖼️ Interface Graphique

L'interface permet à l'utilisateur de :

- Charger une image originale
- Choisir une méthode de tatouage : **LSB**, **DCT**, ou **DWT**
- Insérer un watermark (texte ou image)
- Appliquer le tatouage et visualiser le résultat
- Extraire le watermark à partir d’une image tatouée

---

## 🚀 Lancer le projet

### 1. Prérequis

Installez les dépendances :

```bash
pip install numpy opencv-python matplotlib pillow pywt PyQt5

### 2. Lancer l'application
bash
Copier
Modifier
python interface.py
Note : Assurez-vous que les fichiers d'exemple d’image et de watermark sont présents dans le répertoire ou modifiez les chemins dans l'interface.

##⚙️ Structure du projet
bash
Copier
Modifier
.
├── tatouage.ipynb           # Notebook Jupyter explicatif (version console)
├── interface.py             # Fichier principal pour l’interface graphique
├── watermarking             # Dossier contenant les fonctions LSB, DCT, DWT
│   ├── lsb.py
│   ├── dct.py
│   ├── dwt.py
│   └── utils.py
├── images/                  # Dossier pour stocker les images originales et tatouées
├── README.md


##🔍 Pistes d’amélioration


Ajouter une fonction de chiffrement/déchiffrement du watermark

Ajouter une comparaison quantitative (PSNR, SSIM) entre les méthodes

Support de vidéos (watermarking frame-by-frame)

Tatouage robuste contre les attaques (compression, recadrage, bruit...)

##✅ Conclusion


Ce projet nous a permis de mettre en œuvre différentes techniques de traitement d’image :

Manipulation de bits pour l'insertion discrète (LSB)

Utilisation des transformations fréquentielles (DCT, DWT)

Intégration d’une interface complète avec PyQt5

Développement d’un outil interactif, pédagogique et extensible

Malgré les limites de la méthode LSB en termes de robustesse, la combinaison avec DCT et DWT rend notre application plus fiable pour des cas réels.

📚 Références
Wikipedia – Stéganographie

GeeksforGeeks – Image Watermarking

GitHub – Image Watermarking Project