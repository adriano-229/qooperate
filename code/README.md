# QOOPERATE

Multi-Agent / Public Goods Prisoner's Dilemma — estudio del surgimiento o
colapso de la cooperación en redes de agentes Q-Learning que juegan un
Dilema del Prisionero Iterado con sus vecinos.

Ver `documento_general_de_contexto_del_proyecto.md` para hipótesis y
metodología.

## Instalación

```bash
pip install -e .
```

Instala `qooperate` (en `src/qooperate/`) en modo editable, evitando
`ModuleNotFoundError` sin depender de `PYTHONPATH` ni de configuración
de IDE.

## Diseño: todo es atómico

Cada YAML en `config/` describe una única corrida (una topología, un k,
un alpha, una semilla, ...). No hay listas de barrido en el YAML,
salvo que se generen bins con 0 divisiones. Un barrido de parámetros
(ej. las 3 topologías, o 5 valores de alpha) se arma con **varios**
YAML, uno por combinación, todos con el mismo prefijo antes del primer
`_` (ej. `eX_1.yaml`, `eX_2.yaml`, ...) — ese prefijo determina en qué
carpeta de `results/` cae cada Parquet.

`coop_n_divisions` / `reward_n_divisions` reemplazan a las viejas
listas de bordes de bins: son la cantidad de cortes (divisiones) que
se aplican, equiespaciados, sobre [0,1] (cooperación) y [0,5]
(recompensa, dado el rango de la matriz de pagos T=5..S=0). Con
`n_divisiones=2` (el valor por defecto) se obtienen 3 bins, igual que
antes. `n_divisiones=0` da un único bin (sin discretizar esa variable).

## Uso

### 1. Generar YAMLs interactivamente

```bash
python experiments/generate_yamls.py
```

Pide un nombre de experimento y luego cada parámetro, uno por uno, con
su valor por defecto entre paréntesis (Enter lo acepta tal cual). Se
puede pasar más de un valor por parámetro, separados por espacio — el
script arma el producto cartesiano de todas las combinaciones y
escribe un YAML por combinación en `config/<experimento>/`, nombrando
cada archivo solo con los parámetros que realmente varían. Escribir
`Q` en cualquier prompt cancela la sesión sin generar nada. Valida
cada parámetro (ej. `k` debe ser 4/8/12, `n_agents` debe ser cuadrado
perfecto) y vuelve a pedir el mismo valor si no es válido.

### 2. Correr las corridas

```bash
python experiments/run.py config/eX/eX_1.yaml config/eX/eX_2.yaml
```

Cada YAML se corre de forma independiente; guarda su Parquet en
`results/<prefijo>/<nombre_yaml>.parquet`.

### 3. Generar figuras

```bash
python experiments/figures.py <plot_smoothing> results/eX/eX_*.parquet
```

Por cada Parquet genera 2 PNG **transparentes**, con línea de color
aleatorio: uno de cooperación (`C_t`) y otro de Gini de ventana. Todas
las figuras del mismo tipo comparten tamaño en píxeles y límites de
ejes fijos ([0,1] en Y siempre), sin autoajuste de márgenes, para que
al superponerlas las curvas queden alineadas.

### 4. Superponer figuras

```bash
python experiments/overlay.py salida.png img1.png img2.png ...
```

Composición alfa de 2+ PNG transparentes en una sola imagen. El
usuario es responsable de superponer imágenes compatibles (misma
métrica: todas de cooperación, o todas de Gini — mezclar ambas no
tiene sentido aunque el script no lo impida).

## Tests

```bash
pytest tests/
```
