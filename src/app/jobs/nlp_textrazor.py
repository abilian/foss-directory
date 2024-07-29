import json
import re

import ramda as r
import textrazor
from immutables import Map

from app.extensions import db
from app.models import Page, Societe

TEXTRAZOR_KEY = "410e7b2135f878f5a2814e09afe4bf070048d41f484910ecc680b7ac"
textrazor.api_key = TEXTRAZOR_KEY


def analyse_with_tz(societe: Societe) -> None:
    texts = [get_pages_text(societe, "fr"), get_pages_text(societe, "en")]

    result = tz_analyze_texts(texts)
    societe._entities = json.dumps(result["entities"])
    societe._topics = json.dumps(result["topics"])


def get_pages_text(societe, lang):
    pages = (
        db.session.query(Page)
        .filter(Page.domain == societe.domain, Page.lang == lang)
        .order_by(Page.depth)
        .limit(30)
        .all()
    )
    words = r.map(
        r.pipe(
            lambda page: page.text,
            lambda s: re.sub(r"\s+", " ", s),
            lambda s: s.strip(),
        ),
        pages,
    )
    return "\n".join(words)


def tz_analyze_texts(texts: list[str]) -> dict:
    topic_set = set()
    entity_set = set()

    for text in texts:
        if not text or len(text) < 100:
            continue

        # TZ can only process text < 200 kb
        if len(text) > 150000:
            text = text[0:150000]

        tz_client = textrazor.TextRazor(extractors=["entities", "topics"])
        tz_response = tz_client.analyze(text)

        topics = sorted(tz_response.topics(), key=lambda x: -x.score)
        topics = [topic for topic in topics if topic.score > 0.7]
        for topic in topics:
            topic_set.add(
                Map(
                    {
                        "label": topic.label,
                        "score": topic.score,
                        "wikipedia_link": topic.wikipedia_link,
                        "wikidata_id": topic.wikidata_id,
                    }
                )
            )

        entities = sorted(tz_response.entities(), key=lambda x: -x.confidence_score)
        entities = [
            entity
            for entity in entities
            if entity.confidence_score > 2 and entity.relevance_score > 0.3
        ]
        seen = set()
        for entity in entities:
            if entity.id in seen:
                continue
            seen.add(entity.id)
            if not entity.id:
                continue

            d = {
                "id": entity.id,
                "english_id": entity.english_id,
                "wikidata_id": entity.wikidata_id,
                "relevance_score": entity.relevance_score,
                "confidence_score": entity.confidence_score,
                "dbpedia_types": tuple(entity.dbpedia_types),
                "data": tuple(entity.data),
            }
            entity_set.add(Map(d))

    return {
        "topics": list(dict(x) for x in topic_set),
        "entities": list(dict(x) for x in entity_set),
    }
