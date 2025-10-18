from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Cluster:
    master_key: str                         # clave canónica del maestro
    total_count: int = 0                    # suma de cantidades
    variants: Dict[str, int] = field(default_factory=dict)  # raw_name -> total
    scores: List[float] = field(default_factory=list)       # similitudes usadas
