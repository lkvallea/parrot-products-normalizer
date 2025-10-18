from typing import List, Set, Optional

class Jaccard:
    @staticmethod
    def over_sets(a: Set[str], b: Set[str]) -> float:
        if not a and not b:
            return 1.0
        u = a | b
        return len(a & b) / len(u) if u else 0.0

    @staticmethod
    def over_tokens(a: List[str], b: List[str]) -> float:
        return Jaccard.over_sets(set(a), set(b))

class Damerau:
    """
    Distancia Damerau-Levenshtein con corte temprano por max_dist.
    Devuelve un entero >=0; si excede max_dist, corta y retorna > max_dist.
    """
    def distance(self, s1: str, s2: str, max_dist: int = 2) -> int:
        if s1 == s2:
            return 0
        if abs(len(s1) - len(s2)) > max_dist:
            return max_dist + 1

        # DP con ventana band-limited
        m, n = len(s1), len(s2)
        INF = max_dist + 1
        prev = list(range(n + 1))
        curr = [0] * (n + 1)
        last_row = {}

        for i in range(1, m + 1):
            curr[0] = i
            min_row = curr[0]
            ch1 = s1[i - 1]
            last_match_col = 0
            for j in range(1, n + 1):
                ch2 = s2[j - 1]
                cost = 0 if ch1 == ch2 else 1
                curr[j] = min(
                    prev[j] + 1,        # borrado
                    curr[j - 1] + 1,    # inserción
                    prev[j - 1] + cost  # sustitución
                )
                # transposición
                if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                    curr[j] = min(curr[j], prev[j - 2] + 1)
                min_row = min(min_row, curr[j])

            if min_row > max_dist:
                return INF
            prev, curr = curr, prev  # swap buffers

        return prev[n]
        

class Scorer:
    """
    Combina similitudes:
      score = w_ng * J(ngrams3) + w_tok * J(tokens)
    y valida con DL acotado en zona gris.
    """
    def __init__(self, w_ng: float = 0.6, w_tok: float = 0.4,
                 accept: float = 0.85, gray: float = 0.75, dl_max: int = 2):
        self.w_ng = w_ng
        self.w_tok = w_tok
        self.accept = accept
        self.gray = gray
        self.dl_max = dl_max
        self._jac = Jaccard()
        self._dl = Damerau()

    def score(self,
              tokens_a: List[str], ngrams_a: Set[str], key_a: str,
              tokens_b: List[str], ngrams_b: Set[str], key_b: str) -> float:
        j_ng = self._jac.over_sets(ngrams_a, ngrams_b)
        j_tok = self._jac.over_tokens(tokens_a, tokens_b)
        return self.w_ng * j_ng + self.w_tok * j_tok

    def decision(self,
                 tokens_a: List[str], ngrams_a: Set[str], key_a: str,
                 tokens_b: List[str], ngrams_b: Set[str], key_b: str) -> tuple[float, bool]:
        s = self.score(tokens_a, ngrams_a, key_a, tokens_b, ngrams_b, key_b)
        if s >= self.accept:
            return s, True
        if s >= self.gray:
            dl = self._dl.distance(key_a.replace(" ", ""), key_b.replace(" ", ""), self.dl_max)
            return s, (dl <= self.dl_max)
        return s, False
