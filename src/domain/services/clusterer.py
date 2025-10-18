from typing import Dict, Tuple, Optional
from collections import defaultdict
from src.domain.models.canonicalized import Canonicalized
from src.domain.models.cluster import Cluster
from src.domain.services.blocking import BlockIndex
from src.domain.services.similarity import Scorer

class Clusterer:
    """
    Agrupa claves canónicas por frecuencia descendente.
    - Usa BlockIndex sobre los MAESTROS (no sobre todas las claves)
    - Para cada key candidata, busca mejor maestro y decide con Scorer
    """

    def __init__(self, scorer: Scorer, max_candidates_per_block: int = 20) -> None:
        self.scorer = scorer
        self.index = BlockIndex(max_candidates_per_block=max_candidates_per_block)
        self.masters: Dict[str, Tuple[Canonicalized, Cluster]] = {}  # master_key -> (canon, cluster)

    def _best_master_for(self, cand: Canonicalized) -> Optional[Tuple[str, float]]:
        """
        Devuelve (master_key, score) si algún maestro pasa; si no, None.
        """
        cand_list = self.index.candidates(cand)  # candidatos entre maestros
        best_key = None
        best_score = -1.0
        for mkey, _ in cand_list:
            mcanon, _cluster = self.masters[mkey]
            s, ok = self.scorer.decision(
                cand.tokens, cand.ngrams3, cand.key,
                mcanon.tokens, mcanon.ngrams3, mcanon.key
            )
            if ok and s > best_score:
                best_score, best_key = s, mkey
        if best_key is None:
            return None
        return best_key, best_score

    def fit_from_aggregates(
        self,
        reps: Dict[str, Canonicalized],           # key -> Canonicalized representativo
        key_freq: Dict[str, int],                 # key -> total cantidad
        key_variants: Dict[str, Dict[str, int]],  # key -> {raw: total}
    ) -> Dict[str, Cluster]:
        """
        Construye clusters incrementales:
        - Recorre keys por frecuencia descendente.
        - Si no hay maestro asignable, crea uno nuevo con esa key.
        - Si hay maestro, agrega su frecuencia y variantes.
        """
        # orden por frecuencia descendente
        keys_sorted = sorted(key_freq.keys(), key=lambda k: key_freq[k], reverse=True)

        for key in keys_sorted:
            canon = reps[key]
            best = self._best_master_for(canon) if self.masters else None

            if best is None:
                # Nuevo maestro
                cl = Cluster(master_key=key, total_count=0, variants={}, scores=[1.0])
                self.masters[key] = (canon, cl)
                self.index.add(canon, freq=key_freq[key])

            # Asignación (a sí mismo si fue maestro nuevo, o a otro maestro)
            # Determina el master_key real:
            if best is None:
                master_key = key
                score_used = 1.0
            else:
                master_key, score_used = best

            # Acumula conteos y variantes
            _mcanon, cluster = self.masters[master_key]
            cluster.total_count += key_freq[key]
            for raw, c in key_variants.get(key, {}).items():
                cluster.variants[raw] = cluster.variants.get(raw, 0) + c
            cluster.scores.append(score_used)

        # Salida: master_key -> cluster
        return {mk: cl for mk, (_mc, cl) in self.masters.items()}
