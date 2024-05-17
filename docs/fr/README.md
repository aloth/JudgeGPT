# JudgeGPT - Évaluation des Nouvelles (Fausses)

JudgeGPT est un projet de recherche axé sur l'évaluation critique du contenu des nouvelles générées par l'IA, explorant spécifiquement la perception de l'authenticité dans les nouvelles générées par des machines par rapport à celles générées par des humains. Ce travail en phase initiale vise à recueillir des informations sur la manière dont les individus discernent les nouvelles réelles des nouvelles artificielles.

Si vous êtes intéressé par cette application en action et souhaitez participer à l'évaluation des fausses nouvelles, veuillez visiter notre enquête interactive à l'adresse [https://judgegpt.streamlit.app/](https://judgegpt.streamlit.app/).

## Aperçu du Projet

Le cœur de JudgeGPT réside dans sa plateforme d'enquête interactive, construite avec Streamlit, qui invite les participants à lire des fragments de nouvelles et à évaluer s'ils croient que le contenu est généré par des humains ou des machines. Ce processus est important pour comprendre la perception du public, mais aussi pour affiner les méthodologies de détection et de génération de l'IA dans les développements futurs. Le projet fait partie d'une initiative de recherche plus vaste, complétant notre projet frère [RogueGPT](https://github.com/aloth/RogueGPT), qui se concentre sur la génération de contenus (fausses nouvelles).

## À propos du Nom : JudgeGPT

Le nom JudgeGPT a été soigneusement choisi pour refléter l'objectif principal de ce projet de recherche. Le terme "GPT" est utilisé de manière pars pro toto, où il désigne non seulement les modèles Generative Pre-trained Transformer développés par OpenAI, mais s'étend pour couvrir un large éventail de grands modèles linguistiques (LLMs). Ce choix signifie que, bien que le projet puisse initialement se concentrer sur le contenu généré par les modèles GPT, il est fondamentalement conçu pour évaluer les fragments de nouvelles produits par tout LLM avancé. Le mot "Judge" est utilisé, car il se rapporte directement à l'action effectuée par les participants dans le projet. Les participants sont invités à juger les fragments de nouvelles qui leur sont présentés, en déterminant leur authenticité (réelle vs. fausse) et leur origine (générée par des humains vs. générée par des machines).

### Composants Clés

- `app.py` : Le script principal de l'application qui alimente l'interface web Streamlit, facilitant le processus d'enquête, la collecte de données et l'interaction avec une base de données MongoDB pour le stockage des résultats.

- `requirements.txt` : Un fichier simple listant tous les packages Python nécessaires pour assurer une configuration et un déploiement faciles de l'application JudgeGPT.

## Installation

Pour participer au développement de JudgeGPT, suivez ces étapes :

1. Clonez le dépôt sur votre machine locale.
2. Installez les dépendances requises listées dans `requirements.txt` en utilisant pip :

    ```bash
    pip install -r requirements.txt
    ```

3. Lancez l'application Streamlit :

    ```bash
    streamlit run app.py
    ```

## Utilisation

Lors de l'exécution de l'application, les utilisateurs sont présentés avec une série de fragments de nouvelles récupérés à partir d'une base de données MongoDB. Les participants sont invités à :

1. Lire chaque fragment de nouvelles.
2. Utiliser des curseurs pour évaluer leur perception de l'authenticité du fragment (réel vs. faux) et de sa source (humain vs. machine).
3. Soumettre leur réponse, contribuant ainsi au jeu de données de recherche.

Ce processus itératif permet de collecter des données précieuses sur les perceptions de l'authenticité des nouvelles, alimentant des études analytiques visant à améliorer les cadres de génération et de détection des nouvelles par IA.

### Support Linguistique et Détection de Langue

JudgeGPT vise à fournir une expérience utilisateur personnalisée en déterminant automatiquement votre préférence linguistique pour adapter le contenu de l'enquête en conséquence. Cependant, si vous souhaitez définir manuellement votre langue préférée, vous pouvez facilement le faire dans l'application. De plus, il est possible de spécifier la langue de l'utilisateur via les paramètres de l'URL. Par exemple, pour définir la langue en allemand, vous pouvez utiliser l'URL [https://judgegpt.streamlit.app/?language=de](https://judgegpt.streamlit.app/?language=de), ou pour le français, [https://judgegpt.streamlit.app/?language=fr](https://judgegpt.streamlit.app/?language=fr).

Actuellement, JudgeGPT supporte les langues suivantes :
- Anglais (`en`)
- Allemand (`de`)
- Français (`fr`)
- Espagnol (`es`)

## Statut du Projet

En tant que projet en phase initiale, JudgeGPT évolue continuellement, avec des mises à jour et des améliorations régulières. L'objectif est d'élargir la portée de l'enquête, d'améliorer l'interface utilisateur et de approfondir les aspects analytiques du projet pour fournir des informations plus riches sur la dynamique de l'authenticité des nouvelles à l'ère de l'IA.

## Contribuer

Les contributions à JudgeGPT sont fortement encouragées, que ce soit sous forme d'améliorations de code, d'améliorations de la base de données ou de méthodologies analytiques. Si vous êtes intéressé, veuillez forker le dépôt et soumettre des pull requests avec vos changements proposés.

## Directions Futures et Idées de Mise en Œuvre

Bien que JudgeGPT ait établi un cadre de base pour évaluer les perceptions de l'authenticité des nouvelles, plusieurs idées passionnantes restent à mettre en œuvre. Ces améliorations visent à approfondir l'engagement, à enrichir l'expérience utilisateur et à fournir des perspectives plus nuancées sur les données collectées :

- **Localisation** : Expansion de la plateforme pour supporter plusieurs langues et contenus régionaux, permettant une portée de recherche plus inclusive à l'échelle mondiale. Cela permettrait la collecte de données à travers divers contextes linguistiques et culturels, offrant une compréhension plus riche des perceptions globales de l'authenticité des nouvelles.

- **Gamification** : Introduction d'éléments de gamification pour encourager la participation et rendre le processus d'évaluation plus engageant. Cela pourrait inclure des systèmes de points, des badges ou des classements pour récompenser les utilisateurs pour leurs contributions et leur précision dans l'identification des nouvelles vraies vs. fausses.

- **Résultats (Visualisés)** : Développement d'un tableau de bord interactif où les participants peuvent voir les résultats en temps réel et les perspectives dérivées des données collectives. Cette visualisation rendrait non seulement le projet plus transparent, mais permettrait également aux utilisateurs de comprendre les tendances et les motifs dans la perception des nouvelles.

- **Mécanismes de Retour d'Information Personnalisés** : Offrir aux utilisateurs des retours personnalisés sur leur performance, comme la fréquence à laquelle ils identifient correctement les fausses nouvelles ou comment leurs perceptions s'alignent avec les tendances plus larges. Cela pourrait également éduquer davantage les utilisateurs sur la manière de discerner l'authenticité des nouvelles.

## Licence

JudgeGPT est open-source et disponible sous la licence GNU GPLv3. Pour plus de détails, consultez le fichier LICENSE dans le dépôt.

## Remerciements

Ce projet utilise pymongo pour les interactions avec la base de données.

## Avertissement

JudgeGPT est un projet de recherche indépendant et n'est affilié à, soutenu par ou en aucune manière officiellement connecté à OpenAI. L'utilisation de "GPT" dans le nom de notre projet est purement à des fins descriptives, indiquant l'utilisation de modèles de transformateurs pré-entraînés génératifs comme technologie de base dans notre recherche. Les explorations et les découvertes de notre projet sont les nôtres et ne reflètent pas les vues ou les positions d'OpenAI ou de ses collaborateurs. Nous nous engageons à une recherche en IA responsable et adhérons à des lignes directrices éthiques dans tous les aspects de notre travail, y compris la génération et l'analyse de contenu.
