import sys
from collections import Counter
from typing import Any

import spacy

from app.extensions import db
from app.models import Page, Societe

MODELS = {
    "en": None,
    "fr": None,
}
LANG_TO_MODEL = {
    "en": "en_core_web_md",
    "fr": "fr_core_news_sm",
}


def get_model(lang):
    if MODELS.get(lang):
        return MODELS[lang]

    if lang not in LANG_TO_MODEL:
        return None

    model_name = LANG_TO_MODEL[lang]

    try:
        model = spacy.load(model_name)
    except:
        print(f"Downloading model for lang '{lang}'")
        spacy.cli.download(model_name)
        model = spacy.load(model_name)

    MODELS[lang] = model
    return model


GOOD_LABELS = {
    "ORG",
    "PRODUCT",
    "PERSON",
}


def analyze_with_spacy(societe: Societe) -> Counter:
    entities: Any = Counter()

    pages = (
        db.session.query(Page)
        .filter(Page.domain == societe.domain)
        .filter(Page.text != "")
        .limit(10)
        .all()
    )
    for page in pages:
        # print(page.url, f"(lang={page.lang})")
        sys.stdout.flush()

        nlp = get_model(page.lang)
        if not nlp:
            continue

        text = page.text
        # debug(text)

        doc = nlp(text)
        for ent in doc.ents:
            entity = ent.text.strip()
            label = ent.label_
            if label not in GOOD_LABELS:
                continue
            entities.update([(entity, ent.label_)])
            # print((entity, ent.label_))

    # print()
    # for entity, n in entities.most_common():
    #     print(n, entity)
    # print()

    sys.stdout.flush()
    return entities
