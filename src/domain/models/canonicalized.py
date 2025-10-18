from dataclasses import dataclass
from typing import List, Set

@dataclass(frozen=True)
class Canonicalized:
    tokens: List[str]   # tokens filtrados y singularizados
    key: str            # clave canónica (tokens ordenados, unidos por espacio)
    ngrams3: Set[str]   # 3-gramas de la clave (para etapas siguientes)
