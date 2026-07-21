# QOOPERATE — Experimentos y conclusiones

Este documento resume los experimentos realizados sobre el framework QOOPERATE descrito en `README.md` y las
conclusiones obtenidas.

## Parámetros comunes a todos los experimentos: E0, E1, E2, E3 y EA2

| Parámetro       | Valor |
|-----------------|-------|
| `epsilon`       | 0.1   |
| `gamma`         | 0.9   |
| `rho`           | 1     |
| `reward_window` | 10    |
| `sample_every`  | 10    |

## Parámetros comunes a los experimentos E1, E2, E3 y EA2

Los descritos en la tabla anterior, más:

| Parámetro  | Valor          |
|------------|----------------|
| `n_agents` | 100            |
| `n_rounds` | 12000          |
| `topology` | Watts-Strogatz |
| `k`        | 8              |
| `alpha`    | 0.1            |

## E0 — Validación y calibración

El objetivo de E0 fue verificar la estabilidad del simulador y determinar una duración de corrida adecuada. Se
compararon poblaciones de 100 y 900 agentes, utilizando dos semillas para cada tamaño.

Las curvas de cooperación y Gini fueron prácticamente indistinguibles entre tamaños de población y semillas. La
cooperación comenzó cerca de 0.5, correspondiente a la inicialización aleatoria, y descendió progresivamente hasta
estabilizarse alrededor de 0.05 cerca de la ronda 10000. El Gini mostró una dinámica similar entre corridas y también
alcanzó un régimen estable hacia ese momento.

Se adoptaron entonces `n_rounds=12000` para los experimentos posteriores. Además, se mantuvo `n_agents=100`, ya que
aumentar la población no aportó información adicional apreciable dentro de las configuraciones probadas. Se adoptó un
`smoothing` de 100 (ver comparación entre suavidad de curvas para una misma corrida en Figura 1 y Figura 2).

![exp0_n100_s.png](code/results/figures/exp0/exp0_n100_s.png)
> Figura 1 — E0: Cooperación y Gini para `n_agents=100` para `seed ∈ {123, 3210}`. Smoothing: media móvil de 100 rondas.


![exp0_nB100_s.png](code/results/figures/exp0/exp0_nB100_s.png)
> Figura 2 — E0: Cooperación y Gini para `n_agents=100` para `seed ∈ {123, 3210}`. Smoothing: media móvil de 10 rondas.



![exp0_n900_s.png](code/results/figures/exp0/exp0_n900_s.png)
> Figura 3 — E0: Cooperación y Gini para `n_agents=900` para `seed ∈ {123, 3210}`. Smoothing: media móvil de 100 rondas.

## E1 — Topología y conectividad

Se compararon tres topologías —Lattice, Watts-Strogatz y Erdős-Rényi— con `k ∈ {4, 8, 12}` y dos semillas.

Las tres topologías alcanzaron niveles finales de cooperación prácticamente iguales. Aunque las curvas presentaron
pequeñas diferencias transitorias, ninguna estructura produjo un régimen estacionario claramente distinto.

El grado de conectividad sí afectó ligeramente la velocidad de convergencia: valores mayores de `k` llevaron al sistema
al régimen estacionario algo más rápidamente. Sin embargo, el nivel final de cooperación fue prácticamente independiente
de `k`.

Por lo tanto, H1 no se sostiene. Dentro del rango estudiado, la topología y la conectividad parecen influir
principalmente en la dinámica transitoria, no en el nivel final de cooperación.

![exp1_tla_k.png](code/results/figures/exp1/exp1_tla_k.png)
> Figura 4 — E1: Cooperación y Gini para topologías Lattice con `k ∈ {4 azul, 8 marrón, 12 negro}` y `seed=5`.

![exp1_tws_k.png](code/results/figures/exp1/exp1_tws_k.png)
> Figura 5 — E1: Cooperación y Gini para topologías Watts-Strogatz con `k ∈ {4 negro, 8 verde, 12 violeta}` y `seed=5`.


![exp1_ter_k.png](code/results/figures/exp1/exp1_ter_k.png)
> Figura 6 — E1: Cooperación y Gini para topologías Erdős-Rényi con `k ∈ {4 amarillo, 8 verde, 12 marrón}` y `seed=5`.

## E2 — Tasa de aprendizaje α

Se probaron `α ∈ {0.01, 0.05, 0.1, 0.2, 0.5}` manteniendo fija la configuración de referencia.

Los valores de α modificaron principalmente la velocidad de adaptación. Las tasas mayores llevaron más rápidamente al
régimen estacionario, mientras que las menores produjeron una dinámica algo más lenta. Sin embargo, ninguna
configuración produjo un nivel final de cooperación sustancialmente diferente.

En consecuencia, H2 no recibe apoyo claro. La tasa de aprendizaje afecta la velocidad de convergencia, pero no parece
determinar el régimen colectivo final dentro del rango probado.

![exp2_a0.png](code/results/figures/exp2/exp2_a0.png)
> Figura 7 — E2: Cooperación y Gini para `α ∈ {0.01 rojo, 0.05 violeta, 0.1 rosa, 0.2 amarillo, 0.5 verde}` y `seed=11`.

## E3 — Exploración ε

Se probaron `ε ∈ {0.01, 0.05, 0.1, 0.2, 0.3}`.

Los distintos niveles de exploración modificaron principalmente el ruido y la variabilidad de las curvas. Los valores
mayores de ε mantuvieron una mayor fluctuación, mientras que los valores bajos produjeron trayectorias más suaves. No
obstante, el régimen estacionario final fue esencialmente el mismo.

Por lo tanto, H3 tampoco recibe apoyo claro: no se observó un valor intermedio de ε que sostuviera una cooperación
significativamente mayor.

![exp3_e0.png](code/results/figures/exp3/exp3_e0.png)
> Figura 8 — E3: Cooperación y Gini para `ε ∈ {0.01 verde, 0.05 marrón, 0.1 celeste, 0.2 naranja, 0.3 negro}` y
> `seed=21`.

## EA2 — Profundidad de información del vecindario

El objetivo fue evaluar si proporcionar información de vecinos de orden superior (`ρ > 1`, ver README) favorecía la
cooperación.

El aumento de `rho` produjo una convergencia algo más rápida, pero no modificó sustancialmente el nivel final de
cooperación. La información adicional permitió al agente reaccionar a un entorno más amplio, pero no generó cooperación
sostenida.

Este experimento se corrió con una única semilla por valor de `rho`, a diferencia de E1, E2 y E3, que usaron dos; la
conclusión debe tomarse como preliminar hasta repetirla con más semillas (ver Limitaciones).

![expa2_r.png](code/results/figures/expa2/expa2_r.png)
> Figura 9 — EA2: Cooperación y Gini para `ρ ∈ {1 azul, 2 violeta, 3 verde}` y `seed=44555555`.

## Conclusiones generales

Los resultados muestran cuatro patrones principales.

Primero, la cooperación colapsa hacia niveles bajos en todas las configuraciones estudiadas. Ninguno de los parámetros
barridos logró sostener cooperación alta de forma estable.

Segundo, los parámetros estructurales y de aprendizaje —topología, `k`, `α`, `ε` y `ρ`— afectan principalmente la
velocidad de convergencia y la variabilidad transitoria, pero no el punto de convergencia. En general, una mayor
conectividad, una mayor profundidad del vecindario o una tasa de aprendizaje más alta aceleran la llegada al régimen
estacionario. ε, por su parte, introduce principalmente ruido adicional.

Tercero, el Gini mostró una relación directa con la cooperación. Cuando la cooperación es alta, las recompensas tienden
a ser distintas. Cuando predomina la defección, y viceversa.

Finalmente, la ausencia de cooperación sostenida es consistente con las limitaciones del modelo de agente. El estado
utilizado contiene información agregada del vecindario, pero no conserva la identidad ni el historial individual de cada
vecino. Por lo tanto, el agente no puede implementar mecanismos de reciprocidad directa como Tit-for-Tat, que requieren
recordar y responder al comportamiento de un oponente específico.

## Limitaciones y trabajo futuro

Las principales limitaciones son:

* No se analizó en profundidad el estado interno de los agentes: estados visitados, distribución de valores Q ni grado
  de determinismo de las políticas aprendidas.
* El estado actual no permite reciprocidad directa entre agentes específicos. Incorporar memoria individual o una
  representación explícita de la identidad de los vecinos permitiría estudiar mecanismos de cooperación más cercanos a
  los analizados en la literatura clásica sobre el Dilema del Prisionero Iterado.