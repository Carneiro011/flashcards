# app/services/ai_service.py

import os
import json
from typing import List
from google import genai

from app.models.flashcard import Flashcard, TipoFlashcard


class AIFlashcardService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()

        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY não encontrada.")

        print(f"[AIService] Inicializando com chave: {api_key[:8]}...")
        self.client = genai.Client(api_key=api_key)

        # 🔥 modelo mais seguro hoje
        self.model_name = "gemini-2.0-flash"

    def _montar_prompt(self, texto: str) -> str:
        return f"""
Gere EXATAMENTE 6 flashcards em JSON.

Use tipos:
- verdadeiro_falso
- preencha_lacuna
- pergunta_resposta

Formato:
{{
  "flashcards": [
    {{
      "tipo": "...",
      "frente": "...",
      "verso": "...",
      "conceito": "...",
      "dica": "..."
    }}
  ]
}}

Texto:
{texto}

Retorne SOMENTE JSON.
"""

def gerar_flashcards(self, texto: str, max_cards: int = 5):
    sentencas = self.extrair_sentencas(texto)

    if not sentencas:
        raise ValueError("Texto inválido.")

    flashcards = []
    tipos = list(TipoFlashcard)

    i = 0
    while len(flashcards) < max_cards:
        sentenca = sentencas[i % len(sentencas)]
        tipo = tipos[i % len(tipos)]

        conceito = self.extrair_conceito(sentenca)

        if tipo == TipoFlashcard.VERDADEIRO_FALSO:
            frente = f"É correto afirmar que: {sentenca}?"
            verso = "Verdadeiro."
            dica = f"Revise: {conceito}"

        elif tipo == TipoFlashcard.PREENCHA_LACUNA:
            frente, verso = self.criar_lacuna(sentenca, conceito)
            dica = f"{len(conceito)} letras"

        else:
            frente = f"Explique: {conceito}"
            verso = sentenca
            dica = "Baseie-se no texto."

        flashcards.append(
            Flashcard(
                tipo=tipo,
                frente=frente,
                verso=verso,
                conceito=conceito,
                dica=dica
            )
        )

        i += 1

    return flashcards