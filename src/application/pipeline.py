# src/application/pipeline.py
from collections import Counter, defaultdict
from typing import Tuple
import os
import yaml

from src.infrastructure.io.csv_reader import CSVReader
from src.infrastructure.io.csv_writer import CSVWriter
from src.domain.services.cleaner import Cleaner
from src.domain.services.normalizer import Normalizer
from src.domain.services.similarity import Scorer
from src.domain.services.clusterer import Clusterer

def _load_config(path: str = "etc/config.yaml") -> dict:
    if not os.path.exists(path):
        print(f"[warn] Config no encontrada en {path}. Usando defaults.")
        return {}
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            print("[warn] Config inválida. Usando defaults.")
            return {}
        return data


class Pipeline:
    """
    Pipeline de normalización y agrupación de productos.
    Flujo:
      1) Leer items (CSVReader)
      2) Limpiar y normalizar nombres (Cleaner, Normalizer)
      3) Agregar cantidades por clave canónica
      4) Agrupar por similitud (Clusterer + Scorer)
      5) Escribir CSV final (CSVWriter)
    """

    def __init__(self) -> None:
        # Infra
        self.reader = CSVReader()
        self.writer = CSVWriter()

        # Config
        config = _load_config()

        # Dominio
        self.cleaner = Cleaner()

        # Permite inyectar stopwords/generics/synonyms desde config (todas opcionales)
        norm_cfg = config.get("normalizer", {})
        synonyms = config.get("synonyms", {})  # mantiene tu esquema actual
        stopwords = norm_cfg.get("stopwords")  # si no vienen, Normalizer usa sus defaults
        generic_words = norm_cfg.get("generic_words")

        self.normalizer = Normalizer(
            stopwords=stopwords ,
            generic_words=generic_words ,
            synonyms=synonyms
        )

        # Scorer y Clusterer parametrizables
        scorer_cfg = config.get("scorer", {})
        accept = float(scorer_cfg.get("accept", 0.88))
        gray = float(scorer_cfg.get("gray", 0.80))
        dl_max = int(scorer_cfg.get("dl_max", 2))
        self.scorer = Scorer(accept=accept, gray=gray, dl_max=dl_max)

        clus_cfg = config.get("clusterer", {})
        max_cands = int(clus_cfg.get("max_candidates_per_block", 12))
        self.clusterer = Clusterer(self.scorer, max_candidates_per_block=max_cands)

    def run(self, input_path: str, output_path: str) -> Tuple[int, int]:
        num_rows = 0
        total_input_count = 0

        key_freq = Counter()
        key_variants = defaultdict(Counter)
        reps = {}

        for row in self.reader.stream(input_path):
            num_rows += 1
            total_input_count += row.count
            if num_rows % 100_000 == 0:
                print(f"[info] leídas {num_rows:,} filas…")

            cleaned = self.cleaner.clean(row.raw_name)
            canon = self.normalizer.normalize(cleaned)
            if not canon.key:
                continue

            key_freq[canon.key] += row.count
            key_variants[canon.key][row.raw_name] += row.count
            if canon.key not in reps:
                reps[canon.key] = canon

        clusters = self.clusterer.fit_from_aggregates(reps, key_freq, key_variants)
        self.writer.write_grouped(output_path, clusters)

        return num_rows, total_input_count
