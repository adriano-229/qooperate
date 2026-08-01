# QOOPERATE — Experimentos y conclusiones

Este documento resume los experimentos realizados sobre el framework QOOPERATE descrito en `README.md` y las
conclusiones obtenidas.

**Nota**: La representación gráfica de la Cooperación $C_t$ y el Índice de Gini $G$ se muestran en los gráficos como
línea continua y de trazos, respectivamente.

## E0 — Validación y calibración

Los experimentos en E0 tuvieron como objetivo encontrar una configuración de referencia para los experimentos
posteriores. Se buscó:

1. determinar la cantidad de _semillas_ adecuada para obtener resultados consistentes
3. determinar la cantidad de _agentes_ adecuada para obtener resultados consistentes
2. determinar la cantidad de _rondas_ adecuada para alcanzar régimen estacionario (en caso de que exista)
4. determinar la cantidad de _smoothing_ adecuada para la visualización de las curvas

### Parámetros comunes a E0

Para el experimento E0, todas las corridas compartieron los siguientes parámetros:

| Parámetro          | Valor          |
|--------------------|----------------|
| topology           | watts_strogatz |
| ~~n_agents~~       | _a determinar_ |
| k                  | 8              |
| alpha              | 0.1            |
| epsilon            | 0.1            |
| gamma              | 0.9            |
| rho                | 1              |
| ~~n_seeds~~        | _a determinar_ |
| n_rounds           | 20000          |
| reward_window      | 10             |
| sample_every       | 10             |
| coop_n_divisions   | 2              |
| reward_n_divisions | 2              |
| ws_beta            | 0.1            |
| smoothing          | _a determinar_ |

### Determinación de cantidad de semillas y rondas

Se realizaron corridas con `n_agents ∈ {100, 900}` y `n_seeds=5`, el gráfico resultante es el siguiente:

Con `n_agents=100` y `n_seeds=5`, el gráfico resultante es el siguiente:

![exp0_n100_s.png](code/results/figures/exp0/exp0_n100_s.png)

Con `n_agents=900` y `n_seeds=5`, el gráfico resultante es el siguiente:

![exp0_n900_s.png](code/results/figures/exp0/exp0_n900_s.png)

**Resultados**:

- Se adopta `n_seeds=1` para los experimentos posteriores, ya que las curvas de $C_t$ y $G$ fueron prácticamente
  indistinguibles entre semillas.
- Se adopta `n_rounds=12000` para los experimentos posteriores, ya que $C_t$ y $G$ alcanzan un régimen estable hacia la
  ronda 10000.

### Determinación de cantidad de agentes y smoothing

Se realizaron corridas con `n_agents ∈ {100, 900}` y `smoothing ∈ {10, 100}`.

Con factor de `smoothing=10`, el gráfico resultante es el siguiente:
![exp0_n_sm10.png](code/results/figures/exp0/exp0_n_sm10.png)

Con factor de `smoothing=100`, el gráfico resultante es el siguiente:
![exp0_n_sm100.png](code/results/figures/exp0/exp0_n_sm100.png)

**Resultados**:

- Se adopta `n_agents=100` para los experimentos posteriores, ya que aumentar la población no aportó información
  adicional apreciable.
- Se adopta `smoothing=100` para los experimentos posteriores, ya que es un valor que permite suavizar la curva de forma
  acorde con la cantidad de rondas.

### Conclusiones de E0

Además de los parámetros comunes, se toma como referencia para los experimentos posteriores a los siguientes parámetros:

| Parámetro | Valor |
|-----------|-------|
| n_agents  | 100   |
| n_seeds   | 1     |
| smoothing | 100   |

Por lo tanto, la tabla final de parámetros de comunes para los experimentos posteriores es la siguiente:

| Parámetro          | Valor                                     |
|--------------------|-------------------------------------------|
| ~~topology~~       | _varía en E1, fija en WS para los demás_  |
| n_agents           | 100                                       |
| ~~k~~              | _varía en E1, fija en 8 para los demás_   |
| ~~alpha~~          | _varía en E2, fija en 0.1 para los demás_ |
| ~~epsilon~~        | _varía en E3, fija en 0.1 para los demás_ |
| gamma              | 0.9                                       |
| ~~rho~~            | _varía en EA2, fija en 1 para los demás_  |
| n_seeds            | 1                                         |
| n_rounds           | 12000                                     |
| reward_window      | 10                                        |
| sample_every       | 10                                        |
| coop_n_divisions   | 2                                         |
| reward_n_divisions | 2                                         |
| ws_beta            | 0.1                                       |
| smoothing          | 100                                       |

Notar que los parámetros ~~tachados~~ son los que se específicamente se estudian en los experimentos posteriores.

## E1 — Topología y conectividad

Se realizaron corridas para `topology ∈ {lattice, watts_strogatz, erdos_renyi}` y `k ∈ {4, 8, 12}`.

### Topología fija y conectividad variable

Para `topology=lattice` y `k ∈ {4, 8, 12}`, el gráfico resultante es el siguiente:

![exp1_tla_k.png](code/results/figures/exp1/exp1_tla_k.png)

Para `topology=watts_strogatz` y `k ∈ {4, 8, 12}`, el gráfico resultante es el siguiente:

![exp1_tws_k.png](code/results/figures/exp1/exp1_tws_k.png)

Para `topology=erdos_renyi` y `k ∈ {4, 8, 12}`, el gráfico resultante es el siguiente:

![exp1_ter_k.png](code/results/figures/exp1/exp1_ter_k.png)

**Observaciones**:

- Las 3 topologías alcanzaron niveles finales de $C_t$ y $G$ prácticamente iguales. Aunque las curvas presentaron
  pequeñas diferencias transitorias, ninguna estructura produjo un régimen estacionario distinto.

- El grado de conectividad no afectó significativamente la velocidad ni forma de la convergencia y el nivel final de
  cooperación fue prácticamente independiente de `k`.

## E2 — Tasa de aprendizaje α

Se realizaron corridas para `α ∈ {0.01, 0.05, 0.1, 0.2, 0.5}`, el gráfico resultante es el siguiente:

![exp2_a0.png](code/results/figures/exp2/exp2_a0.png)

**Observaciones**:

- Los valores de α modificaron principalmente la velocidad hacia el equilibrio. Las tasas mayores llevaron más
  rápidamente al régimen estacionario. Sin embargo, ninguna configuración produjo un nivel final de cooperación
  sustancialmente diferente: todas tendían al mismo valor.

## E3 — Exploración ε

Se realizaron corridas para `ε ∈ {0.01, 0.05, 0.1, 0.2, 0.5}`, el gráfico resultante es el siguiente:

![exp3_e0.png](code/results/figures/exp3/exp3_e0.png)

**Observaciones**:

- `ε` afectó de forma similar, pero inversa, a cómo lo hizo `α`. A mayor `ε`, la curva disminuía más lentamente,
  mientras que a menor `ε` la caída era más rápida. Sin embargo, el nivel final de cooperación fue prácticamente
  independiente de
  `ε`. Esto puede describirse debido a las posibilidades, sin éxito para exploradas al fin, de encontrar estrategias
  cooperativas en un entorno que tiende a la defección.

## EA2 — Profundidad de información del vecindario ρ

Se realizaron corridas para `ρ ∈ {1, 2, 5}`, el gráfico resultante es el siguiente:

![expa2_r.png](code/results/figures/expa2/expa2_r.png)

**Observaciones**:

- El aumento de `ρ` produjo una convergencia algo más rápida, pero nuevamente no modificó sustancialmente el nivel final
  de cooperación. La información adicional permitió al agente reaccionar a un entorno más amplio, pero no generó
  cooperación sostenida, sino que al contrario, el efecto de la no-cooperación se propagó más rápidamente.

## Conclusiones

Los resultados muestran que $C_t$ colapsa a niveles bajos en todas las configuraciones. Los parámetros estudiados
afectan principalmente la velocidad de convergencia y la variabilidad transitoria, pero no el régimen estacionario. En
general, una mayor proporción de explotación, conectividad, profundidad del vecindario o tasa de aprendizaje tienden a
acelerar la convergencia.

$G$ presenta una relación directa con la $C_t$: mayores niveles de cooperación se asocian con una mayor desigualdad en
las recompensas.

La ausencia de cooperación sostenida es consistente con una limitación del modelo: el estado agrega la información del
vecindario, pero no conserva la identidad ni el historial de cada vecino. Por ello, los agentes no pueden implementar
mecanismos de reciprocidad directa como Tit-for-Tat. Incorporar memoria individual o la identidad de los vecinos
permitiría estudiar mecanismos de cooperación más cercanos a los de la literatura clásica sobre el dilema del
prisionero, aunque esto implicaría un espacio de estados considerablemente mayor.