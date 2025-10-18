# main.py
import os
import sys
from src.application.pipeline import Pipeline
from src.infrastructure.io.file_check import ensure_exists, ensure_header
from src.infrastructure.io.output_summary import OutputSummary  # resumen final opcional

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    clear_console()

    # Input y output
    input_path = "data/input/test_items_200.csv"
    if len(sys.argv) > 1 and sys.argv[1] in ("200", "1M"):
        input_path = f"data/input/test_items_{sys.argv[1]}.csv"

    output_path = "data/output/products_sold_grouped.csv"

    # Validación mínima
    ensure_exists(input_path)
    ensure_header(input_path, expected="item,count")

    # Ejecutar pipeline
    p = Pipeline()
    num_rows, total_count = p.run(input_path, output_path)

    print(f"\n✅ Proceso completado con éxito.")
    print(f"   Entradas procesadas: {num_rows:,}")
    print(f"   Total count acumulado: {total_count:,}")
    print(f"   Archivo de salida: {output_path}\n")

    # (Opcional) mostrar resumen del CSV resultante
    try:
        OutputSummary.summarize(output_path, top_n=10)
    except Exception as e:
        print(f"(⚠️ Resumen omitido: {e})")

if __name__ == "__main__":
    main()
