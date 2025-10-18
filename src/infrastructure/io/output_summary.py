import csv
from typing import List, Tuple

class OutputSummary:
    """
    Muestra un resumen simple de la salida agrupada.
    - Total de filas
    - Top-N productos
    - Suma total de count
    """

    @staticmethod
    def summarize(path: str, top_n: int = 10) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                rows: List[Tuple[str, int]] = []
                for row in reader:
                    if len(row) != 2:
                        continue
                    try:
                        name, count = row
                        rows.append((name, int(count)))
                    except ValueError:
                        continue

            if not rows:
                print(f"\n⚠️  No hay datos en {path}")
                return

            total = sum(c for _, c in rows)
            print(f"\n📦 Archivo de salida: {path}")
            print(f"   Total de filas: {len(rows)}")
            print(f"   Suma total de count: {total:,}")

            print("\n🏆 Top productos:")
            for name, count in rows[:top_n]:
                print(f"   • {name:<40} {count:>8}")
            print("\n✅ Salida validada.\n")

        except FileNotFoundError:
            print(f"\n❌ Archivo no encontrado: {path}")
