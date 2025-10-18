# 🦜 Parrot Products Normalizer  (blocking + similitud + clustering)

---

## ⚙️ Instalación

```bash
git clone git@github.com:lkvallea/parrot-products-normalizer.git
cd parrot-products-normalizer
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Uso rápido

```bash
python3 main.py #para test_items_200.csv
```
```bash
python3 main.py 1M . #para test_items_1M.csv
```


Parámetros de entrada/salida y reglas viven en `etc/config.yaml`. Los CSV de entrada van en `data/input/` y los resultados en `data/output/`.

---

## 🧩 Estructura del Proyecto

```
parrot-products-normalizer/
├── data/
│   ├── input/                      # Archivos de entrada (.csv)
│   └── output/                     # Resultados procesados
├── etc/
│   └── config.yaml                 # Configuración general del proyecto
├── src/
│   ├── application/
│   │   ├── __init__.py
│   │   └── pipeline.py             # Orquestación del flujo principal
│   ├── domain/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── canonicalized.py
│   │   │   ├── cluster.py
│   │   │   └── product_row.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── blocking.py
│   │   ├── cleaner.py
│   │   ├── clusterer.py
│   │   ├── normalizer.py
│   │   ├── postprocess.py
│   │   └── similarity.py
│   └── infrastructure/
│       ├── __init__.py
│       └── io/
│           ├── __init__.py
│           ├── csv_reader.py
│           ├── csv_writer.py
│           ├── file_check.py
│           └── output_summary.py
├── .gitignore
├── main.py                         # Punto de entrada
├── README.md
└── requirements.txt
```

---

## 🔧 Configuración mínima (`etc/config.yaml`)

```yaml

synonyms:
  revuelto: ["revu3lto","revuel3to","revuellto","rebuelt0","rebuelt","revueltoo","revulto"]
  omelette: ["omellete","omlette","omellet","omelet"]
  pastor: ["pastorr"]
  arrachera: ["arracherra", "arracheraaa"]
  agua: ["agua simple", "agua natural", "h2o"]
  cocacola: ["coke","coca","cola","coca-cola","coca cola"]

  egg: ["eg","eeg","3gg","eggz","eggg","eggz0r"]
  milk: ["milkk","mi1k","miilk","mylk","milc","milkz","mi k","mlik"]
  tomato: ["tomtoe","tomaato","tomoto","tomto","tomatoe","tomat0","t0mat0","tomatoh","tom to"]
  cheese: ["chees","cheeze","cheesee","chese","cheesie","cheeeze","ch33se","chesse"]
  banana: ["banan","banna","bananna","bananah","b4nana","b_nana","b nana","bnana","Bannana"]   
  apple: ["appl3","appl_e","aapl","applle","appl","appel","appple","a-pple","app pel","app pel","apppel","aple","appel"]
  bread: ["br3ad","breaad","breead","briad","braed","bre d","breeed","bred","b r e a d","braead"]   
  lettuce: ["lettus","letuce","lettucee","lettuc","lettc","letucee","lettucez","lettuceh","lettu ce","lettuice","l3ttuce","letuceh","lettu ce","lettuice"]
  onion: ["onon","onionn","oni n","onnion","oni0n","onionz","onyon","un1on","union","0nion","oni n","onin","nion"]  
  orange: ["ornge","orangee","oranj","orenje","0range","or_ng3","or n ge","oragnge","oranje","or nge","Orenge"]

normalizer:
  stopwords: ["de","del","la","el","los","las","con","sin","y","o","en","para","al","d"]
  generic_words: ["taco","tacos","orden","combo","pieza","pz","pzas","paq","paquete","simple","natural","vaso"]


scorer:
  accept: 0.88
  gray: 0.80
  dl_max: 2

clusterer:
  max_candidates_per_block: 12

```

---

## 🔄 Flujo completo

1. **📥 Ingesta**
   - Leer `*.csv`
   - Parsear columnas (`name`, `count`) y normalizar tipos (`count:int`)

2. **🧽 Limpieza (cleaning)**
   - `lowercase`, quitar acentos/símbolos/números irrelevantes
   - eliminar *stopwords* y palabras genéricas
   - tokenizar

3. **🧩 Normalización**
   - singularización simple (“tacos” → “taco”)
   - sinónimos (“cerdo” → “puerco”)
   - orden alfabético de tokens para clave estable
   - generar **clave canónica**

4. **📦 Blocking**
   - agrupar por **prefijo** o clave fonética simple
   - índice de candidatos por bloque
   - n-gramas (3-gramas) para reducir comparaciones

5. **🧮 Similitud**
   - comparar cada producto contra su **bloque de candidatos**
   - *Jaccard* (tokens y n-gramas) + **Levenshtein** (recorte corto)
   - umbral de aceptación (p. ej. **0.85**)

6. **🤝 Agrupación (clustering incremental)**
   - si pasa umbral → agregar al **grupo maestro**
   - si no pasa → crear **nuevo grupo maestro**
   - sumar `count` por grupo

7. **🎨 Postprocesamiento**
   - elegir **nombre representativo** (más frecuente o más “bonito”)
   - calcular **confidence** (media de similitud del grupo)
   - ordenar grupos por frecuencia

8. **📤 Salida**
   - `products_sold_grouped.csv` con `<name,count>`

---

## 🧪 Ejemplo mínimo de E/S

**Entrada (data/input/products_sold.csv):**
```
name,count
Coca-Cola 600ml,12
COCA COLA 0.6L,5
Coca Cola PET 600 ML,8
```

**Salida (data/output/products_sold_grouped.csv):**
```
name,count
coca cola 600 ml,25
```

---

## 🤖 Asistencia Técnica

El diseño y la refactorización se apoyaron con sesiones de revisión asistida por **ChatGPT (modelo GPT-4)** para limpieza de código, revisión de POO y documentación. Las decisiones finales de lógica y arquitectura fueron hechas por el autor.

---

## 🧠 Conocimientos aplicados

- **Python avanzado, POO y diseño modular** (application/domain/services/infrastructure)
- **Pandas** para procesamiento tabular y E/S de CSV
- **Normalización y similitud de strings** (tokens, n-gramas, Jaccard, Levenshtein)
- **Patrones ETL** y **pipelines** reproducibles mediante configuración
