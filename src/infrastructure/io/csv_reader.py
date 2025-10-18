import csv
from typing import Iterator
from src.domain.models.product_row import ProductRow

class CSVReader:
    def __init__(self, delimiter: str = ",", encoding: str = "utf-8"):
        self.delimiter = delimiter
        self.encoding = encoding

    def stream(self, path: str) -> Iterator[ProductRow]:
        with open(path, mode="r", encoding=self.encoding, newline="") as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            if reader.fieldnames != ["item", "count"]:
                raise ValueError(f"Estructura inválida, se esperaban ['item','count'], got {reader.fieldnames}")
            for line in reader:
                item = (line.get("item") or "").strip()
                if not item:
                    continue
                try:
                    count = int(line.get("count", 1))
                except ValueError:
                    count = 1
                yield ProductRow(raw_name=item, count=count)
