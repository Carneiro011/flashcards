# app/models/flashcard.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class TipoFlashcard(Enum):
    """Tipos válidos de flashcard."""
    VERDADEIRO_FALSO = "verdadeiro_falso"
    PREENCHA_LACUNA = "preencha_lacuna"
    PERGUNTA_RESPOSTA = "pergunta_resposta"


@dataclass
class Flashcard:
    """Modelo de flashcard."""
    tipo: TipoFlashcard
    frente: str
    verso: str
    conceito: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dica: Optional[str] = None

    def to_dict(self) -> dict:
        """Converte para dicionário (JSON)."""
        return {
            "id": self.id,
            "tipo": self.tipo.value,
            "frente": self.frente,
            "verso": self.verso,
            "conceito": self.conceito,
            "dica": self.dica,
        }