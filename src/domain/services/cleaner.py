import unicodedata
import re

class Cleaner:
    """
    Limpieza básica de texto para nombres de productos (sin libs externas).
    - Une letras separadas: "b r e a d" -> "bread"
    - Quita dígitos: "br3ad" -> "brad"
    - Quita símbolos (incluye guión bajo "_")
    - Normaliza acentos y espacios
    """

    _re_spaces = re.compile(r"\s+")
    _re_non_letters = re.compile(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]")  # deja solo letras y espacios
    _re_digits = re.compile(r"\d+")
    _re_split_letters = re.compile(r"\b([a-z])\s+([a-z])\b")  # "b r e a d" -> "bread"

    def to_lower(self, s: str) -> str:
        return s.lower()

    def remove_accents(self, s: str) -> str:
        nfkd = unicodedata.normalize("NFKD", s)
        return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

    def remove_digits(self, s: str) -> str:
        return self._re_digits.sub("", s)

    def join_split_letters(self, s: str) -> str:
        """
        Une letras separadas por espacios ("b r e a d" -> "bread")
        y limpia símbolos no alfanuméricos antes de unir.
        """
        # Quita símbolos raros (pero permite guión temporalmente para no romper palabras separadas)
        s = re.sub(r"[^a-z0-9áéíóúñ\s-]", " ", s)
        # Une letras sueltas
        s = self._re_split_letters.sub(r"\1\2", s)
        return s

    def strip_symbols_numbers(self, s: str) -> str:
        # Quita todo lo que no sea letra o espacio (incluye guión y guión bajo)
        return self._re_non_letters.sub(" ", s)

    def collapse_spaces(self, s: str) -> str:
        return self._re_spaces.sub(" ", s).strip()

    def clean(self, s: str) -> str:
        # Orden lógico del procesamiento
        s = self.to_lower(s)
        s = self.remove_accents(s)
        s = s.replace("_", " ")        
        s = s.replace("-", " ") 
        s = self.join_split_letters(s) 
        s = self.remove_digits(s)      
        s = self.strip_symbols_numbers(s)
        s = self.collapse_spaces(s)
        return s
