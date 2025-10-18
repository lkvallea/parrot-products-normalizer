import os

def ensure_exists(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No existe: {path}")

def ensure_header(path: str, expected: str = "item,count") -> None:
    with open(path, "r", encoding="utf-8", newline="") as f:
        header = f.readline().strip()
    if header != expected:
        raise ValueError(f"Header inválido. Esperado '{expected}', encontrado '{header}'")
