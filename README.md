# Travel AI Assistant

Mini-projet Data Science GLSI3 : agent conversationnel multilingue pour une agence de voyage.

Cette première version initialise uniquement l'architecture du projet. Elle ne contient encore ni dataset, ni modèle entraîné, ni implémentation fonctionnelle du chatbot.

## Architecture

```text
travel-ai-assistant/
├── data/
│   ├── raw/                       # Données sources, conservées sans modification
│   ├── processed/                 # Données nettoyées et prêtes pour les modèles
│   └── external/                  # Données provenant de sources ou API tierces
├── models/                        # Artefacts de modèles entraînés (non versionnés)
├── scripts/
│   ├── training/                  # Scripts d'entraînement des futurs modèles
│   └── evaluation/                # Scripts de mesure et de comparaison des modèles
├── src/
│   └── travel_ai_assistant/
│       ├── language_detection/    # Détection de la langue du message
│       ├── travel_filter/         # Filtrage des demandes voyage / hors voyage
│       ├── classification/        # Catégorie et sous-catégorie de la demande
│       ├── ner/                   # Extraction des entités nommées utiles au voyage
│       ├── response_generation/   # Réponse et intégration des API externes
│       └── chatbot/               # Orchestration et future interface Streamlit
└── tests/                         # Tests unitaires et d'intégration
```

Les dossiers `data/` et `models/` contiennent des fichiers `.gitkeep` afin que leur structure soit versionnée, tandis que leurs futurs contenus générés ou volumineux sont ignorés par Git.

## Modules fonctionnels prévus

1. **Détection de langue** : identifier la langue de l'utilisateur pour adapter le traitement et la réponse.
2. **Filtre voyage / hors voyage** : déterminer si la requête appartient au domaine de l'agence.
3. **Classification** : prédire la catégorie puis la sous-catégorie de la demande de voyage.
4. **NER** : extraire les entités telles que destination, dates, budget ou nombre de voyageurs.
5. **Génération de réponse** : construire une réponse contextualisée et interroger, à terme, des API externes.
6. **Interface chatbot** : orchestrer les modules et exposer l'assistant avec Streamlit.

## Technologies prévues

- Python
- scikit-learn pour les modèles classiques et les baselines
- PyTorch et Hugging Face Transformers pour les approches NLP avancées
- Streamlit pour l'interface utilisateur
- Requests pour les futures intégrations d'API HTTP
- Pytest pour les tests

## Installation locale

```bash
python -m venv .venv
```

Sous Windows PowerShell :

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## État du projet

Structure initiale uniquement. L'entraînement, la création de datasets et l'implémentation des modules seront réalisés dans des étapes ultérieures.

