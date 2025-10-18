from typing import Iterable, List, Set, Dict
import re
from src.domain.models.canonicalized import Canonicalized

class Normalizer:
    """
    Normaliza un nombre ya 'limpio' (lower, sin tildes/símbolos):
      - tokeniza
      - filtra stopwords y genéricos
      - singularización simple
      - aplica sinónimos
      - ordena tokens y construye clave canónica
      - genera 3-gramas
    """
    _re_tokens = re.compile(r"\s+")

    def __init__(
        self,
        stopwords: Iterable[str] = None,
        generic_words: Iterable[str] = None,
        synonyms: Dict[str, Iterable[str]] = None,
    ) -> None:
        self.stop: Set[str] = set(stopwords)
        self.generic: Set[str] = set(generic_words)

        # mapa inverso de sinónimos: variante -> canon
        inv: Dict[str, str] = {}
        if synonyms:
            for canon, variants in synonyms.items():
                inv[canon] = canon
                for v in variants:
                    inv[str(v).strip().lower()] = canon
        self.syn_map = inv

    # --- helpers ---
    def _tokenize(self, s: str) -> List[str]:
        s = s.strip()
        if not s:
            return []
        return [t for t in self._re_tokens.split(s) if t]

    def _filter(self, toks: List[str]) -> List[str]:
        return [t for t in toks if t not in self.stop and t not in self.generic]

    def _singular(self, t: str) -> str:
        # reglas muy simples (sin NLP)
        if len(t) > 3 and t.endswith("es") and not t.endswith(("aes","ees","oes")):
            return t[:-2]
        if len(t) > 3 and t.endswith("s"):
            return t[:-1]
        return t

    def _apply_synonyms(self, toks: List[str]) -> List[str]:
        if not self.syn_map:
            return toks
        return [ self.syn_map.get(t, t) for t in toks ]

    def _canonical_key(self, toks: List[str]) -> str:
        return " ".join(sorted(toks))

    def _ngrams3(self, key: str) -> Set[str]:
        s = key.replace(" ", "")
        if len(s) < 3:
            return {s} if s else set()
        return { s[i:i+3] for i in range(len(s)-2) }

    # --- API ---
    def normalize(self, cleaned_name: str) -> Canonicalized:
        toks = self._tokenize(cleaned_name)
        toks = self._filter(toks)
        toks = [self._singular(t) for t in toks]
        toks = self._apply_synonyms(toks)
        key = self._canonical_key(toks)
        grams = self._ngrams3(key)
        return Canonicalized(tokens=toks, key=key, ngrams3=grams)
