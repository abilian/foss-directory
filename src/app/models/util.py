from __future__ import annotations

import nltk

sentence_detector = nltk.data.load("tokenizers/punkt/french.pickle")


def make_tagline(description):
    sentences = sentence_detector.tokenize(description)
    if sentences:
        result = sentences[0]
        if len(result) > 120:
            result = result[0:117] + "..."
        return result
    else:
        return ""
