"""Percepción del agente: normalización del texto antes de clasificar.

Implementa lo descrito en el artículo (Sec. IV-A): se acortan las letras repetidas,
los enlaces se reemplazan por un marcador y los emojis se convierten en palabras.
La misma función se usa en entrenamiento, evaluación y en el servicio, para que el
modelo vea siempre el mismo tipo de entrada.
"""
from __future__ import annotations

import re

import emoji

_URL = re.compile(r"https?://\S+|www\.\S+")
_USER = re.compile(r"@\w+")
_REPEAT = re.compile(r"(\w)\1{2,}")          # "buenooooo" -> "buenoo"
_SPACES = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = text or ""
    text = _URL.sub(" url ", text)
    text = _USER.sub(" @usuario ", text)
    text = emoji.demojize(text, language="es", delimiters=(" ", " "))
    text = text.replace("_", " ")
    text = _REPEAT.sub(r"\1\1", text)
    return _SPACES.sub(" ", text).strip()
