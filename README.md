Projet Traitement d’Images : Tatouage Numérique
Réalisé par : Dhia Roueg & Mohamed Amine Gharbi GI1-S1
Introduction
Le tatouage numérique (ou watermarking) est une technique consistant à insérer une information (texte, image, signature, etc.) dans un fichier multimédia (image, son, vidéo) de manière discrète, afin de garantir l'authenticité, la traçabilité ou la protection contre le piratage.

Ce projet a pour but d’implémenter et d’expérimenter une méthode de tatouage numérique sur des images en utilisant Python et des bibliothèques de traitement d’image.


Nos solutions
I. Tatouage numérique sur des images
Méthodologie
Ajout du watermark :

Chargement de l’image originale.

Préparation du watermark (texte ou image à insérer).

Conversion du watermark en niveaux de gris et en binaire.

Insertion du watermark dans les bits de poids faible (LSB) des pixels de l’image originale.

Sauvegarde de l’image tatouée.

Extraction et vérification du watermark :

Chargement de l’image tatouée.

Récupération des bits de poids faible.

Reconstruction du watermark à partir des données extraites.

Comparaison avec le watermark d’origine pour vérifier l’authenticité.

Utilisation
Exécuter le notebook tatouage.ipynb dans un environnement Jupyter. Les différentes étapes du tatouage et de l’extraction sont séparées en cellules. Vous pouvez modifier les chemins des images à traiter directement dans les cellules.

Librairies utilisées
numpy

opencv-python

matplotlib

PIL (facultatif)

Pistes d’amélioration
Support d’images de tailles différentes via redimensionnement automatique.

Ajout d’un watermark textuel ou dynamique (nom, date, signature...).

Chiffrement du watermark pour plus de sécurité.

Utilisation d’une méthode de tatouage robuste (DCT, DWT...).

Conclusions
Ce projet nous a permis de mettre en pratique des notions importantes de traitement du signal, notamment :

La manipulation des bits dans les pixels.

L’intégration d’informations sans altérer l’aspect visuel d’une image.

L’évaluation de la robustesse et de la fidélité d’un tatouage numérique.

Malgré les limites du tatouage par LSB en termes de sécurité, ce projet constitue une excellente base pédagogique pour aborder les principes du watermarking.


Sources / Références
https://fr.wikipedia.org/wiki/St%C3%A9ganographie

https://www.geeksforgeeks.org/image-watermarking-using-python/

https://github.com/anhquan0412/image-watermarking
