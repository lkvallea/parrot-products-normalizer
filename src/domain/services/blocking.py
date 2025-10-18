from collections import defaultdict
from typing import Dict, List, Tuple, Set, Optional
from src.domain.models.canonicalized import Canonicalized

class SimplePhonetic:
    """
    Codifica una clave canónica a una forma fonética simple:
    - quita vocales internas (mantiene 1ª y última letra si son vocales)
    - comprime consonantes repetidas
    - quita espacios
    """
    _v = set("aeiou")

    def encode(self, key: str) -> str:
        s = key.replace(" ", "")
        if not s:
            return s
        out = []
        prev = ""
        for i,ch in enumerate(s):
            is_vowel = ch in self._v
            keep = (i == 0) or (i == len(s)-1) or (not is_vowel)
            if keep:
                if ch != prev:
                    out.append(ch)
                    prev = ch
        return "".join(out)

def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

class BlockIndex:
    """
    Índice para reducir comparaciones:
      - por primera letra
      - por clave fonética simple
      - ranking por Jaccard de 3-gramas
    Guarda solo claves canónicas únicas (no filas)
    """
    def __init__(self, max_candidates_per_block: int = 20):
        self.max_cands = int(max_candidates_per_block)
        self.phon = SimplePhonetic()

        self.by_first: Dict[str, Set[str]] = defaultdict(set)  # 'a' -> {key,...}
        self.by_phon:  Dict[str, Set[str]] = defaultdict(set)  # 'rrchr' -> {key,...}
        self.key_ngrams: Dict[str, Set[str]] = {}              # key -> ngrams
        self.freq: Dict[str, int] = {}                         # key -> frecuencia (para priorizar)

    def add(self, canon: Canonicalized, freq: int = 1) -> None:
        key = canon.key
        if key in self.key_ngrams:
            self.freq[key] = self.freq.get(key, 0) + freq
            return
        self.key_ngrams[key] = set(canon.ngrams3)
        self.freq[key] = int(freq)
        first = key[0] if key else ""
        self.by_first[first].add(key)
        self.by_phon[self.phon.encode(key)].add(key)

    def candidates(self, canon: Canonicalized, limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Devuelve [(key_candidata, score_jaccard_ngrams)], ordenado desc."""
        key = canon.key
        first = key[0] if key else ""
        phon_k = self.phon.encode(key)

        pool = set()
        pool |= self.by_first.get(first, set())
        pool |= self.by_phon.get(phon_k, set())

        # no te propongas a ti mismo
        pool.discard(key)

        # rank por jaccard de n-gramas + desempate por frecuencia
        scored = []
        grams_q = set(canon.ngrams3)
        for k in pool:
            score = jaccard(grams_q, self.key_ngrams.get(k, set()))
            scored.append((k, score))

        # ordena por score desc y luego por frecuencia desc
        scored.sort(key=lambda t: (t[1], self.freq.get(t[0], 0)), reverse=True)
        lim = limit or self.max_cands
        return scored[:lim]
