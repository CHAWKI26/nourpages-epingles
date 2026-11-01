# nourpages-epingles

Images des épingles Pinterest de [NourPages](https://nourpages.com), au format 1000 × 1500 px.

- `images/AAAA-MM/` : les images publiées, une par épingle. Make les télécharge depuis leur adresse publique :
  `https://raw.githubusercontent.com/CHAWKI26/nourpages-epingles/main/images/AAAA-MM/<fichier>.jpg`
- `make_pin.py` : le générateur (Python + Pillow), aux couleurs NourPages (bleu nuit, or, crème).
- `fonts/` : les polices Lora et Inter (licence SIL OFL 1.1, voir `fonts/OFL.txt`).

## Utilisation

```
python3 make_pin.py <dossier_de_sortie> <specs.json>
```

`specs.json` est une liste d'épingles :

```json
[{"file": "mon-slug-1.jpg", "label": "SANTÉ & BIEN-ÊTRE", "title": "Titre court\nsur deux lignes",
  "subtitle": "(sous-titre)", "bullets": ["Point 1", "Point 2", "Point 3"],
  "cta": "Lire l’article  →", "note": "Inspiré du livre « … »"}]
```

Ne supprimez pas d'images déjà publiées : les épingles Pinterest en ont besoin.
