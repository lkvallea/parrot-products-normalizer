import csv
from typing import Dict, List, Tuple, Optional
from src.domain.models.cluster import Cluster
from src.domain.services.postprocess import DisplayNamePicker

class CSVWriter:
    """
    Escribe name,count.
    Usa DisplayNamePicker para elegir el nombre presentable.
    """
    def __init__(self, picker: Optional[DisplayNamePicker] = None) -> None:
        self.picker = picker or DisplayNamePicker()

    def write_grouped(self, path: str, clusters: Dict[str, Cluster]) -> None:
        rows: List[Tuple[str, int]] = []
        for _mk, cl in clusters.items():
            name = self.picker.choose_display_name(cl)
            rows.append((name, cl.total_count))
        rows.sort(key=lambda t: t[1], reverse=True)  # ordenar por count desc

        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["name", "count"])
            w.writerows(rows)
