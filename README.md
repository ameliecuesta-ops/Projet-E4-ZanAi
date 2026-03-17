
# Projet : Agent IA pour la cybersécurité & Détection Brute Force

Ce projet consiste à utiliser un agent ia qui détecte 3 attaques différentes et bloque les ip malveillantes

## Inventaire des fichiers

[predict_new.py] -> scanner de détection automatique 

  -Il charge l'IA : Il réveille ton modèle Random Forest et ses réglages pour qu'ils soient prêts à travailler.
  -Il nettoie les données : Il lit tes logs réseau par petits morceaux et remplace les erreurs ou les cases vides par des 0.
  -Il traque les attaques : Il analyse chaque ligne et lève une alerte dès qu'il est sûr à plus de 30% qu'il s'agit d'une menace.
  -Il fait le bilan : Il enregistre toutes ses découvertes dans un fichier predictions.csv et affiche le score final.
  
  En résumé : C'est l'outil qui transforme une liste de connexions brutes en une liste d'alertes de sécurité.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[train_model.py] -> C'est l'étape de fabrication du cerveau (l'entraînement) de l'IA :

  -Il prépare les données : Il nettoie ton fichier dataset.csv et met toutes les valeurs à la même échelle pour que l'IA ne soit pas confuse.
  -Il apprend : Il utilise l'algorithme "Random Forest" pour apprendre à faire la différence entre une connexion normale et une attaque.
  -Il s'auto-évalue : Il teste ses propres performances sur des données qu'il n'a jamais vues pour vérifier sa précision.
  -Il enregistre tout : Il sauvegarde le "cerveau" (random_forest_model.pkl) et les réglages de nettoyage (scaler.pkl) pour qu'ils soient utilisés par ton script de détection.

  En résumé : C'est le script qui crée l'intelligence que tu utiliseras plus tard pour détecter les menaces.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[tools.py] -> C'est le "bras armé" de l'agent. Ce fichier transforme ton script de détection en une fonction que l'IA peut appeler toute seule :

  -Il emballe le moteur ML : Il reprend toute la logique de predict_new.py (chargement du modèle, nettoyage des données, calcul du seuil à 0.3) pour en faire une fonction unique nommée detect_attacks().
  -Il automatise l'analyse : Au lieu de lancer un script à la main, l'agent peut maintenant demander : "Exécute detect_attacks sur le fichier nouveau_dataset.csv".
  -Il fait le rapport à l'IA : Une fois l'analyse terminée, il renvoie un résumé textuel (nombre d'attaques et pourcentage) que l'agent pourra ensuite t'expliquer avec des mots simples.

  En résumé : C'est le connecteur qui permet à ton agent GPT de devenir un véritable analyste capable d'utiliser tes outils de détection.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[test_echantillon.py] -> C'est ton outil de vérification rapide. Il sert à tester si ton intelligence artificielle fonctionne bien sur un tout petit échantillon avant de lancer de grosses analyses :

  -Il crée un test miniature : Il prend seulement les 5 premières lignes de ton fichier nouveau_dataset.csv pour aller très vite.
  -Il simule une analyse : Il applique exactement le même nettoyage (remplissage des vides, mise à l'échelle) que le vrai script de détection.
  -Il affiche les probabilités : Au lieu de juste dire "Attaque" ou "Sain", il te montre le score précis (ex: 0.85) pour chaque ligne.
  -Il valide le seuil : Il vérifie si, avec ton seuil de 0.3, ces 5 lignes sont bien classées comme des attaques ou non.

  En résumé : C'est un "bac à sable" pour s'assurer que tes fichiers .pkl et ton code de nettoyage sont corrects sans attendre des heures.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[test_chunks.py] -> C'est ton outil de vérification de la lecture des données. Il sert à s'assurer que ton ordinateur arrive à lire ton gros fichier CSV sans saturer sa mémoire vive (RAM) :

  -Il teste le découpage : Il vérifie que le système de "bouchées" (chunks) de 10 000 lignes fonctionne correctement.
  -Il compte les lignes : Pour chaque morceau lu, il affiche le nombre de lignes trouvées et le numéro du bloc.
  -Il valide le format : Il affiche les noms des colonnes pour être sûr que le fichier nouveau_dataset.csv est bien structuré comme prévu.
  -Il fait le total : À la fin, il te donne le nombre exact de lignes analysées pour confirmer que rien n'a été oublié en route.

  En résumé : C'est un test de "tuyauterie" pour être sûr que tes données circulent bien jusqu'à l'IA sans erreur de lecture.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[scaler.pkl] -> C'est le fichier de réglages mathématiques de ton projet.

  -Il harmonise les données : Dans ton dataset, certaines colonnes ont de très grands nombres et d'autres des tout petits. Le scaler les ramène tous sur la même échelle (souvent entre 0 et 1) pour que l'IA ne soit pas perturbée.
  -Il garde la mémoire des proportions : Il a enregistré la "moyenne" et "l'écart-type" de tes données d'entraînement.
  -Il garantit la cohérence : Il permet d'appliquer exactement les mêmes transformations aux nouveaux logs qu'à ceux utilisés lors de l'apprentissage, pour que l'IA compare ce qui est comparable.

 En résumé : C'est la "règle de mesure" qui permet à ton IA de lire les données correctement sans faire d'erreur d'interprétation.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[random_forest_model.pkl] -> C'est le "Cerveau" de ton projet : le modèle d'intelligence artificielle entraîné.

  -Il contient l'expérience : Ce fichier a mémorisé toutes les caractéristiques des attaques (volumes de paquets, durée des flux, ports utilisés) apprises durant l'exécution de train_model.py.
  -Algorithme Random Forest : Il fonctionne comme une armée de centaines d'arbres de décision qui votent tous ensemble pour décider si une activité est "Saine" ou une "Attaque".
  -Prise de décision : Lorsqu'il reçoit de nouvelles données, il calcule une probabilité de menace. C'est ce score qui est ensuite comparé à ton seuil de 0.3 dans tes outils de détection.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[RAG.txt] -> C'est ta bibliothèque de savoir (la base de connaissances).

Ce fichier est le cœur de la partie RAG (Retrieval-Augmented Generation) de ton projet. Il contient les informations textuelles que l'IA va consulter pour "réfléchir" :

  -Définitions : Il explique ce qu'est le RAG et comment l'IA utilise des vecteurs pour comprendre le contexte.
  -Règles métier : Il définit ce qu'est une attaque brute force (ex: plus de 5 échecs en 1 minute).
  -Playbooks (Procédures) : Il donne les étapes à suivre pour un analyste SOC quand une attaque est détectée (ex: bloquer l'IP, isoler le compte).
  -Exemples de code : Il contient même des morceaux de code pour montrer comment transformer ce texte en vecteurs.

 En résumé : C'est le "manuel d'instruction" de ton agent. Sans ce fichier, l'IA peut détecter des chiffres, mais elle ne sait pas pourquoi c'est grave ni quoi faire pour réparer le problème.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[build_vectors.py]  -> C'est ton indexeur de connaissances. Il sert à transformer ton fichier texte en une base de données que l'IA peut "fouiller" instantanément :

  -Il lit ton savoir : Il ouvre ton fichier RAG.txt qui contient tes définitions et procédures cyber.
  -Il découpe en morceaux : Il divise le texte en petits blocs (chunks) de 300 caractères pour que l'IA puisse retrouver précisément l'info dont elle a besoin.
  -Il traduit en chiffres : Il utilise un modèle (HuggingFace) pour transformer ces morceaux de texte en vecteurs mathématiques (embeddings).
  -Il crée la base : Il enregistre le tout dans un dossier ./zanai_knowledge_base. C'est cette base que l'agent interrogera pour expliquer une attaque.

  En résumé : C'est le script qui donne de la "mémoire" et de la "culture cyber" à ton agent.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[langchain_agent.py]  ->  C'est le chef d'orchestre (l'Agent). C'est lui qui donne un visage humain à toute ta technologie en discutant avec toi.

  -Il incarne un rôle : Il est configuré avec un "System Prompt" pour agir comme un expert analyste SOC.
  -Il utilise tes outils : Il importe ta fonction detect_attacks (via le fichier tools.py) et la transforme en un outil qu'il peut décider d'utiliser seul s'il juge que ta question nécessite une analyse de données.
  -Il réfléchit et répond : Il utilise le modèle GPT-4o-mini. Quand tu lui demandes "Combien d'attaques y a-t-il ?", il ne répond pas au hasard : il appelle l'outil de détection, récupère les chiffres, et te rédige une réponse structurée.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

[load_rag.py]  ->  C'est le testeur de lecture.

Son rôle est très simple mais indispensable : il sert à vérifier que ton fichier de connaissances RAG.txt est bien lisible par ton code Python avant d'essayer de le transformer en base de données.

  -Il ouvre le fichier : Il vérifie que le chemin et l'encodage (UTF-8) sont bons.
  -Il mesure le contenu : Il affiche le nombre total de caractères pour être sûr que le fichier n'est pas vide.
  -Il affiche un aperçu : Il imprime les 500 premiers caractères à l'écran pour confirmer que le texte n'est pas corrompu (caractères bizarres, etc.).

  En résumé : C'est une vérification de sécurité pour s'assurer que la source de ton savoir est prête à être indexée par build_vectors.py.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 📝 Ce qu'il reste à faire (Roadmap)

1) faire les chunks en utilisant le rag
2) créer fonction: detect_attack(log) que l’agent pourra utiliser (sortie de la fonction=bruteforce ou rien
3) recherche rag : Quand une attaque est détectée :
                          chercher dans la base RAG :

4) Créer la fonction pour bannir une IP
5) Créer l’agent LangChain
              L’agent doit avoir 3 outils :
                   1 detect_attack
                   2 search_rag
                   3 ban_ip


[Logique de l’agent]
Si :detect_attack = bruteforce

alors :
chercher explication dans RAG
demander autorisation user
bannir IP



[Réponse finale de l’agent]

Attack detected: brute force
Source IP: 192.168.1.10

Explanation:
A brute force attack is repeated login attempts…

Action:
IP banned
Faire la meme chose pour injection sql et denial of service



