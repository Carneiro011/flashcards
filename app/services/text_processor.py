import re
import random
from typing import List
from app.models.flashcard import Flashcard, TipoFlashcard


class TextProcessor:

    def extrair_sentencas(self, texto: str) -> List[str]:
        sentencas = re.split(r'[.!?]\s+', texto.strip())

        sentencas = [
            s.strip()
            for s in sentencas
            if len(s.split()) >= 4
        ]

        if not sentencas:
            return [texto.strip()]

        return sentencas

    def extrair_conceito(self, sentenca: str) -> str:
        stopwords = {
            'a','o','as','os','um','uma','uns','umas',
            'de','da','do','das','dos','em','no','na',
            'e','é','são','foi','ser','estar','que','se'
        }

        palavras = sentenca.split()
        candidatos = []

        for palavra in palavras:
            limpa = re.sub(r'[^\w]', '', palavra.lower())
            if limpa not in stopwords and len(limpa) > 3:
                candidatos.append(palavra)

        return " ".join(candidatos[:2]) if candidatos else palavras[0]

    def tornar_falsa(self, sentenca: str) -> str:
        substituicoes = {
            " é ": " não é ",
            " são ": " não são ",
            " pode ": " não pode ",
            " aumenta ": " diminui ",
            " maior ": " menor ",
            " sempre ": " nunca ",
            " fundamental ": " irrelevante ",
            " importante ": " insignificante "
        }

        for k, v in substituicoes.items():
            if k in sentenca:
                return sentenca.replace(k, v, 1)

        return sentenca + " (afirmação incorreta)"

    def criar_lacuna(self, sentenca: str, conceito: str):
        frente = re.sub(
            re.escape(conceito),
            "______",
            sentenca,
            count=1,
            flags=re.IGNORECASE
        )

        return frente, conceito

    def normalizar_sentenca(self, s: str) -> str:
        return s[0].upper() + s[1:] if s else s

    def gerar_flashcards(self, texto: str, max_cards: int = 6):
        sentencas = self.extrair_sentencas(texto)
        random.shuffle(sentencas)

        flashcards = []

        tipos = [
            TipoFlashcard.VERDADEIRO_FALSO,
            TipoFlashcard.VERDADEIRO_FALSO,
            TipoFlashcard.PREENCHA_LACUNA,
            TipoFlashcard.PREENCHA_LACUNA,
            TipoFlashcard.PERGUNTA_RESPOSTA,
            TipoFlashcard.PERGUNTA_RESPOSTA,
        ]

        for i in range(max_cards):
            sentenca = sentencas[i % len(sentencas)]
            conceito = self.extrair_conceito(sentenca)
            sentenca = self.normalizar_sentenca(sentenca)

            tipo = tipos[i]

            if tipo == TipoFlashcard.VERDADEIRO_FALSO:

                if random.random() < 0.5:
                    frente = sentenca
                    verso = "Verdadeiro"
                else:
                    falsa = self.tornar_falsa(sentenca)
                    frente = falsa
                    verso = "Falso"

                dica = f"Analise: {conceito}"

            elif tipo == TipoFlashcard.PREENCHA_LACUNA:
                frente, verso = self.criar_lacuna(sentenca, conceito)
                dica = f"{len(conceito)} letras"

            else:
                frente = f"Explique: {conceito}"
                verso = sentenca
                dica = "Baseie-se no texto"

            flashcards.append(
                Flashcard(
                    tipo=tipo,
                    frente=frente,
                    verso=verso,
                    conceito=conceito,
                    dica=dica
                )
            )

        random.shuffle(flashcards)
        return flashcards