import re
from typing import Dict, List
from src.domain.models.cluster import Cluster

class DisplayNamePicker:
    """
    Elige un nombre representativo para el cluster:
      1) Variante ORIGINAL más frecuente (con tildes, etc.)
      2) Limpia cuantificadores/sobrantes (2pz, #3, (), etc.)
      3) Quita dígitos, guiones, guiones bajos y símbolos
      4) Colapsa espacios y aplica title-case ligero en español
    """

    # Quita cantidades como "2pz", "#3", paréntesis vacíos o con contenido
    _re_quantifiers = re.compile(
        r"(\b\d+\s*(pz|pzas|pza|pieza|piezas)\b|#\d+|\(\s*\)|\(\s*[^)]*\s*\))",
        re.IGNORECASE
    )
    # Solo permite letras y espacios (admite acentos). Elimina dígitos, '_', '-', etc.
    _re_symbols_nums = re.compile(r"[^a-záéíóúñ\s]", re.IGNORECASE | re.UNICODE)
    _re_spaces = re.compile(r"\s+")

    _lower_small = {
        "de","del","la","el","los","las","con","sin","y","o","en","para","al","por","a"
    }

    def _best_variant(self, variants: Dict[str, int]) -> str:
        """Variante original más frecuente."""
        return max(variants.items(), key=lambda kv: kv[1])[0] if variants else ""

    def _strip_extras(self, s: str) -> str:
        """
        Limpieza de la variante elegida para mostrar:
         - quita cuantificadores (2pz, #3, () )
         - reemplaza '-' y '_' por espacio
         - elimina cualquier dígito o símbolo, dejando solo letras/espacios
         - colapsa espacios
        """
        s = self._re_quantifiers.sub(" ", s)
        s = s.replace("-", " ").replace("_", " ")   # 👈 fuera guiones y guiones bajos
        s = self._re_symbols_nums.sub(" ", s)       # 👈 fuera números y símbolos
        s = self._re_spaces.sub(" ", s).strip()
        return s

    def _pretty_case_es(self, s: str) -> str:
        # Title-case ligero: palabras “pequeñas” en minúsculas, resto Capitaliza
        if not s:
            return s
        parts = s.split()
        fixed: List[str] = []
        for i, w in enumerate(parts):
            wl = w.lower()
            if i != 0 and wl in self._lower_small:
                fixed.append(wl)
            else:
                fixed.append(wl.capitalize())
        return " ".join(fixed)

    def choose_display_name(self, cluster: Cluster) -> str:
        name = self._best_variant(cluster.variants) or cluster.master_key
        name = self._strip_extras(name)
        name = self._spaces_guard(name)
        name = self._pretty_case_es(name)
        return name

    def _spaces_guard(self, name: str) -> str:
        # evita string vacío por sobre-limpieza
        return name if name else "Producto"

def confidence(cluster: Cluster) -> float:
    """Promedio de scores de similitud del cluster (0..1). Si solo maestro: 1.0 por diseño."""
    if not cluster.scores:
        return 0.0
    return sum(cluster.scores) / len(cluster.scores)
