from dataclasses import dataclass

@dataclass(frozen=True)
class ProductRow:
    raw_name: str
    count: int
