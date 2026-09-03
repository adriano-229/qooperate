# 1. Introducción

La cooperación entre individuos constituye un problema central en el estudio de sistemas formados por agentes que
persiguen sus propios intereses. Cuando no existe una autoridad central que obligue a los individuos a cooperar, surge
la pregunta de bajo qué condiciones puede aparecer y mantenerse un comportamiento cooperativo. Este problema ha sido
estudiado desde distintas disciplinas y constituye uno de los problemas clásicos de la teoría de juegos. En particular,
Robert Axelrod planteó el estudio de la cooperación mediante interacciones repetidas entre individuos que, considerados
aisladamente, tienen incentivos para actuar de manera no cooperativa.

Una de las herramientas utilizadas para estudiar este problema es el Dilema del Prisionero. En su formulación iterada,
dos agentes pueden elegir repetidamente entre cooperar y desertar, de manera que las consecuencias de una acción
dependen también de la decisión tomada por el otro participante. La estructura del juego introduce una tensión entre el
beneficio colectivo de la cooperación y el incentivo individual de obtener una recompensa mayor mediante la deserción.
La repetición del juego permite, además, que las decisiones presentes tengan consecuencias sobre interacciones futuras y
que puedan surgir comportamientos adaptativos basados en experiencias anteriores.

El estudio de estos fenómenos adquiere una dimensión adicional cuando las interacciones no ocurren entre una única
pareja de agentes, sino dentro de una población conectada mediante una red. En este contexto, la estructura de la red
determina qué individuos pueden interactuar directamente. La cooperación, por lo tanto, no depende únicamente de la
estructura de recompensas del juego, sino también de la dinámica colectiva producida por las interacciones entre
múltiples agentes.

En este trabajo, los agentes no siguen estrategias predefinidas, sino que aprenden mediante aprendizaje por refuerzo. En
particular, se utiliza el algoritmo Q-Learning para asociar valores a pares estado-acción y actualizar progresivamente
las decisiones a partir de las recompensas obtenidas. A diferencia de un escenario de aprendizaje con un único agente,
los agentes de este sistema aprenden simultáneamente y modifican continuamente el entorno de los demás participantes. El
proyecto considera, por ello, un entorno multiagente no estacionario, en el que no se presupone que el proceso de
aprendizaje deba converger necesariamente a una política óptima.

Este proyecto estudia precisamente este comportamiento: una población de agentes juega repetidamente el Dilema del
Prisionero sobre una red y aprende sus decisiones mediante Q-Learning. Cada agente interactúa con sus vecinos y utiliza
información sobre su entorno para construir su estado, mientras que sus acciones y las de los demás modifican las
condiciones de las interacciones posteriores. De esta manera, el sistema permite estudiar conjuntamente el efecto de la
estructura de interacción, la información disponible y los parámetros del aprendizaje sobre el comportamiento colectivo.

El objetivo inicial del trabajo consistió en identificar condiciones bajo las cuales pudieran emerger comportamientos
cooperativos y no cooperativos, estudiando particularmente la influencia de la topología de la red y de la información
local disponible sobre la velocidad de convergencia y el nivel de cooperación alcanzado. Sin embargo, los experimentos
correspondientes a esta primera etapa produjeron resultados cualitativamente similares: independientemente de las
configuraciones estudiadas, el sistema mostró una tendencia generalizada hacia la no cooperación. Esta observación
modificó el foco del trabajo. En lugar de continuar buscando combinaciones de parámetros capaces de producir
cooperación, se incorporó una segunda etapa destinada a estudiar cómo los agentes habían aprendido el comportamiento que
finalmente ejecutaban.

Así, el análisis pasó de considerar únicamente el comportamiento observable del sistema a examinar también su dinámica
interna de aprendizaje. Para ello, además de medir la evolución de la cooperación y de las recompensas, se analizaron
los valores relativos de las acciones aprendidas mediante la diferencia

$$
\Delta Q (s)=Q (s,C)-Q (s,D),
$$

junto con la frecuencia con la que los agentes visitaron cada estado. Esta información permite distinguir entre una
preferencia aprendida por una determinada acción y la importancia efectiva de cada estado dentro de la dinámica de la
simulación.

El trabajo se organiza en dos etapas experimentales relacionadas. La primera analiza el efecto de distintos parámetros
del entorno y del algoritmo de aprendizaje sobre el comportamiento colectivo. Se estudian la topología de interacción,
la tasa de aprendizaje, el nivel de exploración, la profundidad del vecindario considerado y la representación del
estado. La segunda profundiza en los resultados obtenidos en la primera etapa mediante el análisis de los valores Q y de
la distribución de visitas a los estados, con el objetivo de caracterizar con mayor detalle el proceso mediante el cual
emerge el comportamiento observado.

El propósito final no es demostrar que la cooperación sea imposible en sistemas multiagente, sino caracterizar qué
ocurre bajo el modelo concreto implementado y determinar qué papel desempeñan sus diferentes componentes. En particular,
la persistencia de la no cooperación constituye un resultado que debe ser explicado en relación con la información
disponible para los agentes, la dinámica del aprendizaje y la estructura de las interacciones.

# 2. Marco teórico

## 2.1. Teoría de juegos y el Dilema del Prisionero

La teoría de juegos proporciona un marco formal para estudiar situaciones en las que el resultado obtenido por un agente
depende no solamente de sus propias decisiones, sino también de las decisiones tomadas por otros agentes. En este tipo
de problemas, cada participante debe seleccionar sus acciones teniendo en cuenta que los demás también persiguen
determinados objetivos.

El Dilema del Prisionero constituye uno de los modelos clásicos para estudiar el conflicto entre el interés individual y
el beneficio colectivo. En su formulación de dos jugadores, cada participante dispone de dos acciones posibles: cooperar
`C` o desertar (no cooperar) `D`. Por definición, la estructura de recompensas debe satisfacer las relaciones

$$
T > R > P > S
$$

y

$$
2R > T+S,
$$

donde `T` (_del inglés: temptation_) representa la recompensa obtenida al desertar frente a un oponente que coopera, `R`
(_reward_) la recompensa de la cooperación mutua, `P` (_punishment_) la recompensa de la deserción mutua y `S`
(_sucker_) la recompensa obtenida al cooperar frente a un oponente que deserta.

La primera desigualdad establece el orden de preferencia individual característico del dilema. Para un jugador, obtener
`T` resulta mejor que obtener `R`, que a su vez es mejor que `P`, mientras que `S` constituye el peor resultado. La
segunda desigualdad expresa que la cooperación mutua proporciona un beneficio conjunto superior al obtenido mediante la
alternancia entre cooperación y deserción.

En consecuencia, existe una tensión fundamental entre el resultado individualmente preferible y el resultado
colectivamente beneficioso. Si el otro jugador coopera, desertar proporciona `T`, superior a `R`; si el otro jugador
deserta, desertar proporciona `P`, superior a `S`. Por lo tanto, la deserción constituye la mejor respuesta individual
independientemente de la acción del oponente. Sin embargo, ambos jugadores obtienen una recompensa mayor mediante la
cooperación mutua que mediante la deserción mutua.

El proyecto utiliza la matriz canónica

$$
T=5,\qquad R=3,\qquad P=1,\qquad S=0,
$$

que satisface las condiciones anteriores.

Esta estructura es particularmente relevante para el estudio de sistemas multiagente porque permite observar cómo las
decisiones individualmente racionales pueden producir un resultado colectivo inferior al que sería posible mediante
coordinación.

## 2.2. Dilema del Prisionero Iterado y cooperación

En el Dilema del Prisionero de una única interacción, los jugadores no necesitan considerar consecuencias posteriores de
sus decisiones. La situación cambia cuando el juego se repite. En el Dilema del Prisionero Iterado (IPD), los mismos
agentes pueden interactuar sucesivamente, de manera que las decisiones tomadas durante rondas anteriores pueden influir
en las decisiones posteriores.

La iteración introduce así la posibilidad de reciprocidad. Un agente puede cooperar inicialmente y continuar cooperando
si el otro también lo hace, o puede responder a una deserción mediante una deserción posterior. De esta manera, la
repetición permite que aparezcan comportamientos que no serían posibles o relevantes en una única interacción.

Este problema constituye precisamente el punto de partida para Axelrod. Su investigación se centra en la pregunta de
bajo qué condiciones puede surgir cooperación entre individuos egoístas cuando no existe una autoridad central que
obligue a los participantes a cooperar. Para estudiarla, Axelrod utilizó el IPD y organizó torneos computacionales en
los que diferentes estrategias competían entre sí.

Uno de los resultados más conocidos de estos torneos fue el desempeño de TIT FOR TAT. Esta estrategia comienza
cooperando y, posteriormente, reproduce la acción realizada por el oponente en la ronda anterior. Axelrod señala que TIT
FOR TAT obtuvo el mejor resultado en la primera ronda del torneo y volvió a ganar en la segunda, a pesar de competir con
estrategias considerablemente más complejas.

Este resultado es importante para el presente trabajo por dos motivos. Primero, muestra que la estructura del IPD
iterado permite que la cooperación pueda mantenerse mediante mecanismos de reciprocidad, aun cuando cada jugador tenga
incentivos individuales para desertar. Segundo, establece una referencia conceptual con la cual comparar un sistema
donde los agentes no poseen una estrategia explícita, sino que deben aprender su comportamiento mediante interacción.

## 2.3. Condiciones para la estabilidad de la cooperación

El análisis de Axelrod no está limitado a determinar qué estrategia obtuvo mejores resultados en los torneos. También
estudia las condiciones bajo las cuales una estrategia cooperativa puede mantenerse frente a estrategias alternativas.

Una de las variables utilizadas para representar la importancia de las interacciones futuras es el factor de descuento
$w$. Un valor elevado de $w$ implica que las recompensas futuras tienen un peso relativamente importante respecto de las
recompensas inmediatas. Esto resulta relevante para la cooperación porque una estrategia puede aceptar un beneficio
inmediato menor si esto permite conservar una relación cooperativa beneficiosa en rondas posteriores.

Para los valores

$$
T=5,\qquad R=3,\qquad P=1,\qquad S=0,
$$

Axelrod obtiene, para la estabilidad colectiva de TIT FOR TAT, la condición

$$
w \geq \max\left (\frac{T-R}{T-P}, \frac{T-R}{R-S} \right).
$$

Con los valores anteriores,

$$
w \geq \max\left (\frac{5-3}{5-1}, \frac{5-3}{3-0} \right)
= \max\left (\frac12,\frac23 \right)
= \frac23.
$$

Por lo tanto, para este conjunto de recompensas, la estabilidad de TIT FOR TAT requiere un peso suficientemente elevado
de las interacciones futuras.

Este resultado proporciona una referencia útil para interpretar el IPD como un problema dinámico. La cooperación no
depende únicamente de que exista un beneficio colectivo, sino también de que las interacciones futuras tengan suficiente
importancia como para hacer rentable mantener una relación recíproca.

Sin embargo, este resultado no puede trasladarse directamente al modelo de este proyecto. En el análisis de Axelrod, las
estrategias disponen de la **historia de la interacción** y pueden responder específicamente al comportamiento del
oponente. TIT FOR TAT, por ejemplo, conserva información sobre la acción realizada por el otro jugador en la ronda
anterior. En este proyecto, en cambio, el estado utilizado por cada agente resume información agregada de su vecindario
y no conserva la identidad individual ni el historial completo de cada vecino. Esta diferencia será relevante
posteriormente al discutir la ausencia de cooperación sostenida.

## 2.4. Aprendizaje por refuerzo

El aprendizaje por refuerzo (Reinforcement Learning, RL) estudia problemas en los que un agente aprende a seleccionar
acciones mediante su interacción con un entorno. En lugar de recibir explícitamente la acción correcta para cada
situación, el agente obtiene recompensas como consecuencia de sus decisiones y utiliza dichas experiencias para
modificar su comportamiento.

En términos generales, el agente observa un estado $s$, selecciona una acción $a$, recibe una recompensa $r$ y alcanza
un nuevo estado $s'$. El objetivo del aprendizaje consiste en desarrollar una política que permita obtener buenas
recompensas acumuladas.

Una formulación clásica de este problema utiliza los procesos de decisión de Markov (MDP), en los cuales se define un
conjunto de estados, acciones, recompensas y transiciones. El enfoque de aprendizaje por refuerzo permite resolver
también situaciones en las que las funciones de recompensa y transición no son conocidas inicialmente.

Una diferencia importante respecto de métodos supervisados es que el agente no recibe directamente una etiqueta que
indique qué acción debería haber elegido. La información utilizada para modificar la política proviene de las
consecuencias de sus propias decisiones.

## 2.5. Q-Learning

Q-Learning es un algoritmo de aprendizaje por refuerzo basado en valores. En lugar de representar directamente una
política, mantiene una función $Q (s,a)$ que estima el valor esperado de ejecutar la acción $a$ cuando el agente se
encuentra en el estado $s$.

La regla de actualización resulta

$$
Q (s,a)\leftarrow Q (s,a)+ \alpha \left[
r+\gamma\max_{a'}Q (s',a')-Q (s,a)
\right],
$$

donde:

* $s$ es el estado actual;
* $a$ es la acción seleccionada;
* $r$ es la recompensa obtenida;
* $s'$ es el estado posterior;
* $\alpha$ es la tasa de aprendizaje;
* $\gamma$ es el factor de descuento;
* $a'$ representa las posibles acciones disponibles en el nuevo estado.

La expresión entre corchetes representa el error de diferencia temporal utilizado para modificar el valor aprendido. El
término

$$
r+\gamma\max_{a'}Q (s',a')
$$

representa una estimación del retorno obtenido a partir de la experiencia actual y del mejor valor esperado en el estado
siguiente. La actualización desplaza $Q (s,a)$ en dirección a esa estimación, con una magnitud determinada por
$\alpha$.

En el presente proyecto, cada agente dispone de valores Q para las acciones de cooperación y deserción en los estados
que puede observar. Por ello, una forma particularmente útil de analizar el aprendizaje consiste en comparar
directamente ambos valores mediante

$$
\Delta Q (s)=Q (s,C)-Q (s,D).
$$

Si

$$
\Delta Q (s)>0,
$$

el agente asigna mayor valor a cooperar en ese estado; si

$$
\Delta Q (s)<0,
$$

la deserción posee mayor valor aprendido. Esta medida constituye posteriormente una de las herramientas principales del
análisis interno de los experimentos.

El comportamiento no depende exclusivamente de los valores Q, ya que durante el aprendizaje el agente debe balancear
exploración y explotación. Para ello se utiliza una política $\epsilon$-greedy: con una determinada probabilidad el
agente explora una acción, mientras que en el resto de los casos selecciona la acción asociada al mayor valor Q. El
parámetro $\epsilon$ es también uno de los factores estudiados experimentalmente.

## 2.6. Aprendizaje multiagente

La aplicación de aprendizaje por refuerzo a múltiples agentes introduce una dificultad: cada agente modifica el entorno
en el que los demás están aprendiendo.

En un problema de un único agente, las transiciones y recompensas pueden modelarse bajo determinados supuestos como
propiedades del entorno. En un sistema multiagente, en cambio, las acciones de los demás participantes forman parte de
aquello que determina la evolución del entorno. Si esos participantes también están aprendiendo, sus políticas cambian
con el tiempo.

Por este motivo, las garantías clásicas de convergencia de Q-Learning en determinados escenarios de un solo agente no
pueden trasladarse directamente al aprendizaje multiagente, ya que una modificación en el comportamiento de un agente
puede cambiar las recompensas y los estados experimentados por sus vecinos, quienes a su vez actualizan sus propios
valores Q. Por ello, el sistema se estudia como una dinámica adaptativa multiagente y no como la búsqueda de una
solución óptima de un MDP.

## 2.7. Aprendizaje, reciprocidad e información disponible

La comparación entre el enfoque de Axelrod y el modelo de este proyecto permite identificar una diferencia conceptual
central. En los experimentos de Axelrod, las estrategias pueden utilizar explícitamente la historia de las interacciones
con un oponente determinado. TIT FOR TAT constituye el ejemplo más sencillo: coopera inicialmente y posteriormente imita
la acción anterior del oponente.

Aquí se utiliza, en cambio, una representación agregada del entorno. El agente observa características de su vecindario
y utiliza dicha información para construir su estado, pero no mantiene una representación individualizada de cada
vecino. En consecuencia, el sistema no implementa directamente un mecanismo de reciprocidad equivalente a TIT FOR TAT.

Esta diferencia no implica que la cooperación sea imposible en el modelo, pero sí modifica los mecanismos mediante los
cuales podría surgir. Una estrategia basada en reciprocidad individual requiere distinguir quién cooperó, quién desertó
y cómo respondió cada participante en interacciones anteriores. Cuando esa información se agrega en variables de
vecindario, diferentes historias pueden producir el mismo estado observable.

# 3. Diseño experimental

## 3.1. Descripción del sistema

QOOPERATE modela una población de agentes que juega repetidamente el Dilema del Prisionero sobre una red. Cada agente
interactúa con los agentes que forman parte de su vecindario y, a partir de la información observada y de las
recompensas obtenidas, aprende mediante Q-Learning qué acción seleccionar en cada situación.

El proceso de aprendizaje y el proceso de interacción ocurren simultáneamente. No existe una fase de entrenamiento
separada de una fase posterior de ejecución. En cada ronda, cada agente selecciona una de las dos acciones disponibles,
cooperación `C` o deserción `D`. Las recompensas obtenidas dependen de las acciones realizadas durante la interacción.
Posteriormente, el agente observa nuevamente su entorno, construye el siguiente estado y actualiza el valor
correspondiente a la acción ejecutada mediante la regla de Q-Learning.

La política de selección de acciones utiliza $\epsilon$-greedy. Con probabilidad $\epsilon$, el agente explora una
acción, mientras que con probabilidad $1-\epsilon$ selecciona la acción con mayor valor Q para el estado observado. De
esta manera, el comportamiento del sistema depende tanto de los valores aprendidos como del grado de exploración
mantenido durante la simulación.

## 3.2. Representación del estado

El estado de cada agente se construye a partir de información sobre su entorno y su comportamiento reciente. El modelo
dispone de cuatro variables discretizadas:

* $s_1$: acción mayoritaria observada en el vecindario durante la ronda anterior.
* $s_2$: última acción realizada por el propio agente.
* $s_3$: tasa de cooperación observada en el vecindario durante la ronda anterior.
* $s_4$: recompensa media reciente del propio agente.

La representación utilizada puede incorporar progresivamente estas variables. Se consideran cuatro configuraciones:

$$
S1 = (s_1)
$$

$$
S12 = (s_1,s_2)
$$

$$
S123 = (s_1,s_2,s_3)
$$

$$
S1234 = (s_1,s_2,s_3,s_4).
$$

![states.png](code/report/states.png)

La representación $S1234$ constituye la configuración más completa, mientras que $S1$ contiene únicamente la información
sobre la acción mayoritaria del vecindario.

Con la representación completa, las primeras dos variables poseen dos valores posibles, mientras que la tasa de
cooperación y la recompensa discretizadas poseen tres niveles. Por lo tanto, el espacio de estados contiene

$$
2\times2\times3\times3=36
$$

estados posibles.

Esta representación permite estudiar si el hecho proporcionar información adicional sobre el contexto en el que se
encuentra el agente modifica la política aprendida o distribuye el aprendizaje entre un número mayor de estados.

## 3.3. Estructura de la red

Los agentes se organizan mediante una red cuyos nodos representan agentes y cuyos enlaces determinan las relaciones de
vecindad. La topología de la red controla qué agentes pueden interactuar directamente y, por tanto, qué información
local está disponible para cada participante.

Se consideran tres modelos de red:

* **Lattice:** estructura regular en la que cada agente mantiene conexiones con un conjunto fijo de vecinos.
* **Watts-Strogatz:** red que combina estructura local con cierto grado de aleatoriedad mediante el proceso de rewiring.
* **Erdős-Rényi:** red generada mediante conexiones aleatorias entre los agentes.

![topologies.png](code/report/topologies.png)

Además de la topología, se modifica la profundidad del vecindario considerada por el agente. Se define un parámetro
$\rho$, donde $\rho=1$ corresponde a los vecinos directos, mientras que valores superiores incorporan agentes situados a
mayores distancias dentro de la red.

En los experimentos se consideran

$$
\rho\in\{1,2,4\}.
$$

De esta forma, la estructura experimental permite distinguir entre el efecto de la topología de la red y el efecto de
ampliar la cantidad de información espacial disponible para cada agente.

## 3.4. Métricas de comportamiento colectivo

La primera etapa del análisis se centra en el comportamiento observable de la población. Entre las principales medidas
se encuentra la proporción de cooperación en cada ronda $t$,

$$
C_t=\frac{\text{número de agentes que cooperan en }t} {\text{número total de agentes}},
$$

que permite estudiar la evolución temporal de la cooperación.

También se analiza la desigualdad en las recompensas obtenidas por los agentes mediante el coeficiente de Gini, denotado
como $G$. Esta medida permite complementar el análisis de la cooperación observando cómo se distribuyen las recompensas
entre los participantes.

Estas métricas permiten caracterizar el resultado colectivo, pero no explican por sí mismas cómo los agentes llegaron a
dicho comportamiento. Por este motivo, la segunda etapa del análisis incorpora información directamente relacionada con
los valores Q y las visitas a los estados.

## 3.5. Análisis interno del aprendizaje

Para estudiar la dinámica interna del aprendizaje se registra, en distintos momentos de la simulación, el valor Q
asociado a las dos acciones disponibles en cada estado.

La medida principal utilizada es

$$
\Delta Q (s)=Q (s,C)-Q (s,D).
$$

Esta diferencia permite identificar la preferencia aprendida para cada estado. Un valor positivo indica una mayor
valoración de la cooperación, mientras que un valor negativo indica una mayor valoración de la deserción.

Sin embargo, la magnitud de $\Delta Q$ no indica por sí misma qué importancia tiene un estado dentro del comportamiento
global. Un estado puede presentar una fuerte preferencia por una acción y, al mismo tiempo, ser visitado muy pocas
veces.

Para incorporar esta dimensión se registra también la frecuencia relativa de visitas,

$$
F (s)=\frac{V (s)}{\sum_{s'}V (s')},
$$

donde $V (s)$ representa el número de visitas acumuladas al estado $s$.

La combinación de ambas medidas se expresa mediante

$$
P (s)=\Delta Q (s)\,F (s).
$$

Esta medida permite ponderar la preferencia aprendida por la frecuencia con la que el estado aparece durante la
simulación. En consecuencia, un estado con una gran magnitud de $\Delta Q$ pero una frecuencia muy baja tendrá una
influencia menor sobre $P$ que un estado frecuentemente visitado con una preferencia comparable.

Los valores de $\Delta Q$, $F$ y $P$ se registran en distintos puntos del proceso de aprendizaje. Esto permite observar cómo se modifica progresivamente la importancia de los diferentes estados.

## 3.6. Calibración inicial

Antes de estudiar sistemáticamente los parámetros de interés se realizó un experimento de calibración, denominado E0. Su
objetivo fue determinar una configuración de simulación suficientemente representativa para los experimentos
posteriores.

La configuración inicial utilizó una red Watts-Strogatz con $k=8$, $\alpha=0.1$, $\epsilon=0.1$, $\gamma=0.9$,
$\rho=1$, 20.000 rondas y una representación de estado $S1234$. Se probaron poblaciones de 100 y 900 agentes utilizando
cinco semillas.

A partir de esta calibración se observó que las curvas de cooperación y desigualdad obtenidas con distintas semillas
eran prácticamente indistinguibles. Por este motivo, para los experimentos posteriores se utilizó una única semilla.

También se observó que las métricas colectivas alcanzaban un régimen estable aproximadamente alrededor de la ronda
10.000. En consecuencia, se redujo la duración de las simulaciones a 12.000 rondas, manteniendo un margen suficiente
para observar el régimen estable.

Finalmente, se compararon distintos niveles de suavizado de las curvas. Se adoptó un suavizado de 100 rondas,
considerado adecuado para visualizar la evolución temporal sin introducir un nivel excesivo de ruido.

La población utilizada posteriormente fue de 100 agentes, dado que el incremento a 900 agentes no proporcionaba
información adicional apreciable para los objetivos del estudio.

## 3.7. Diseño de los experimentos

Una vez establecida la configuración de referencia mediante E0, se realizaron cinco experimentos principales. En cada
uno se modificó una dimensión específica mientras se mantuvieron constantes las demás condiciones, con el objetivo de
aislar su influencia sobre la dinámica del sistema.

### E1: efecto de la topología

E1 analiza el efecto de la estructura de la red comparando las topologías Erdős-Rényi, Lattice y Watts-Strogatz. El
objetivo es determinar si una modificación de la estructura de interacción produce diferencias apreciables en la
evolución de la cooperación y en el aprendizaje de los agentes.

### E2: efecto de la tasa de aprendizaje

E2 estudia la influencia de la tasa de aprendizaje $\alpha$. Se consideran los valores

$$
\alpha\in\{0.001,0.005,0.01,0.05,0.2\}.
$$

La comparación permite estudiar si la rapidez con la que los nuevos resultados modifican los valores Q afecta únicamente
la velocidad de convergencia o también el comportamiento colectivo alcanzado.

### E3: efecto de la exploración

E3 modifica el parámetro $\epsilon$ de la política $\epsilon$-greedy mediante los valores

$$
\epsilon\in\{0.01,0.05,0.1,0.2,0.5\}.
$$

El objetivo es determinar cómo el compromiso entre exploración y explotación afecta la diversidad de estados visitados y
la consolidación de una política determinada.

### E4: efecto de la profundidad del vecindario

E4 estudia la cantidad de información espacial disponible para los agentes mediante

$$
\rho\in\{1,2,4\}.
$$

Se busca determinar si observar únicamente los vecinos directos o incorporar información de agentes situados a mayores
distancias modifica la dinámica de aprendizaje.

### E5: efecto de la representación del estado

Finalmente, E5 compara las representaciones

$$
S1,\quad S12,\quad S123,\quad S1234.
$$

Este experimento permite estudiar el efecto de la cantidad y naturaleza de la información utilizada para definir un
estado. En particular, se analiza si una representación más detallada permite al agente distinguir situaciones que
quedan agrupadas bajo representaciones más simples y si esto modifica el comportamiento emergente.

## 3.8. Estrategia de análisis

Los experimentos se analizan en dos niveles complementarios.

En primer lugar, se considera el comportamiento colectivo mediante la evolución de la cooperación y de la distribución
de recompensas. Este nivel permite determinar qué comportamiento emerge globalmente a partir de las interacciones entre
los agentes.

En segundo lugar, se analiza la información interna generada por Q-Learning mediante $\Delta Q$, $F$ y $P$. El objetivo
es identificar qué estados adquieren importancia durante el aprendizaje, qué acciones son preferidas en ellos y cómo
cambia su relevancia a lo largo de la simulación.

Esta segunda perspectiva resulta especialmente importante debido al resultado obtenido en la primera etapa experimental.
Dado que las diferentes configuraciones produjeron una tendencia generalizada hacia la no cooperación, el análisis de
los valores Q y de las visitas a los estados permite estudiar el proceso mediante el cual dicha tendencia se consolida.

Por tanto, el análisis no se limita a determinar si los agentes cooperan o desertan al final de una simulación. También
busca caracterizar la dinámica que conduce a ese resultado y determinar qué diferencias introducen los parámetros
estudiados.

# 4. Análisis y discusión de resultados

## 4.1. Consideraciones generales

Los experimentos realizados muestran un comportamiento cualitativamente consistente: bajo las configuraciones
estudiadas, los agentes desarrollan una marcada tendencia hacia la deserción. Ninguna de las variaciones analizadas
produce una transición sostenida hacia un régimen cooperativo.

Sin embargo, esta conclusión general no implica que todos los parámetros carezcan de influencia. Las modificaciones
introducidas afectan principalmente la dinámica mediante la cual el sistema alcanza su estado final. En particular,
cambian la velocidad de convergencia, la concentración de las visitas en determinados estados y la magnitud de la
preferencia aprendida entre cooperar y desertar.

Esta distinción resulta importante para interpretar los resultados. El comportamiento colectivo final es relativamente
robusto frente a las variaciones estudiadas, mientras que el proceso de aprendizaje que conduce a dicho comportamiento
presenta diferencias apreciables.

## 4.2. E0: calibración de la simulación

El experimento E0 tuvo como objetivo determinar una configuración adecuada para las simulaciones posteriores. La
comparación entre diferentes tamaños de población y semillas mostró que aumentar el número de agentes no proporcionaba
información cualitativamente diferente y que las curvas obtenidas con distintas semillas eran prácticamente
indistinguibles.

A partir de estos resultados se adoptó una población de 100 agentes y una única semilla para los experimentos
posteriores. También se redujo la duración de las simulaciones a 12.000 rondas, dado que las métricas colectivas
alcanzaban un régimen estable aproximadamente alrededor de la ronda 10.000.

La calibración permitió, por tanto, reducir el costo computacional sin perder las características relevantes del
comportamiento observado. Esta configuración constituye la referencia sobre la cual se construyen E1–E5.

## 4.3. E1: efecto de la topología

El primer experimento estudió si la estructura de la red modificaba el comportamiento aprendido. Se compararon las
topologías Erdős-Rényi, Lattice y Watts-Strogatz manteniendo constantes los demás parámetros.

El resultado más destacable es la similitud entre las tres configuraciones. En todos los casos, el aprendizaje termina
favoreciendo la deserción y las visitas se concentran progresivamente en el estado $ (1,1,0,0)$. Al final de la
simulación, este estado concentra aproximadamente entre el 55 % y el 57 % de las visitas según la topología.

Por lo tanto, las diferencias estructurales entre las tres redes no se traducen en una diferencia cualitativa en el
comportamiento emergente. La topología puede introducir pequeñas variaciones en determinados valores Q —por ejemplo,
aparece en Lattice un estado secundario con una preferencia cooperativa marginal—, pero estas diferencias no adquieren
suficiente peso como para modificar el resultado colectivo.

Este resultado constituye una primera evidencia de la robustez de la tendencia hacia la no cooperación. En las
condiciones estudiadas, cambiar la estructura de las conexiones no resulta suficiente para generar un régimen
cooperativo.

## 4.4. E2: efecto de la tasa de aprendizaje

E2 muestra una diferencia más clara respecto de E1. Al modificar $\alpha$, el resultado cualitativo continúa siendo no
cooperativo, pero cambia considerablemente la velocidad y el grado de concentración del aprendizaje.

Con valores muy bajos de $\alpha$, especialmente $\alpha=0.001$, las visitas permanecen distribuidas entre numerosos
estados incluso al final de la simulación. No se observa un atractor claramente dominante, lo que indica que el
aprendizaje es demasiado lento para consolidarse completamente dentro del horizonte temporal utilizado.

A medida que aumenta $\alpha$, la concentración en el estado $ (1,1,0,0)$ se vuelve progresivamente más pronunciada.
Con $\alpha=0.05$, este estado alcanza aproximadamente el 86 % de las visitas, mientras que con $\alpha=0.2$ alcanza
alrededor del 74 %.

El resultado más importante de E2 es, por tanto, que la tasa de aprendizaje modifica principalmente la dinámica de
convergencia y no el comportamiento hacia el cual converge el sistema. Una tasa baja mantiene durante más tiempo una
distribución diversa de estados, mientras que tasas mayores permiten consolidar rápidamente una política no cooperativa.

Además, el aumento de $\alpha$ no produce un crecimiento indefinido de la magnitud de $\Delta Q$. En el estado
dominante, por ejemplo, los valores finales se mantienen aproximadamente en el mismo orden de magnitud. Esto sugiere que
el principal efecto de $\alpha$ en estas simulaciones no consiste en generar valores Q cada vez mayores, sino en
acelerar la incorporación de las experiencias al comportamiento aprendido.

## 4.5. E3: efecto de la exploración

El experimento E3 analiza el efecto de $\epsilon$, parámetro que controla el equilibrio entre exploración y explotación.

El comportamiento obtenido presenta una relación no lineal. Con valores extremadamente bajos de exploración, como
$\epsilon=0.01$, los agentes no llegan a concentrar sus visitas en un único estado. Aunque la mayoría de los estados
frecuentes presentan una preferencia por la deserción, la distribución permanece relativamente dispersa.

En el rango intermedio, particularmente con $\epsilon=0.1$ y $\epsilon=0.2$, aparece la mayor concentración en $
(1,1,0,0)$. Este estado alcanza aproximadamente el 56 % de las visitas para $\epsilon=0.1$ y el 66 % para
$\epsilon=0.2$.

El comportamiento cambia nuevamente con $\epsilon=0.5$. La exploración permanente mantiene una distribución
considerablemente más amplia de estados y evita que uno de ellos domine de manera tan marcada.

Por lo tanto, E3 muestra que la exploración no determina por sí misma si el sistema será cooperativo o no cooperativo.
En cambio, regula la posibilidad de consolidar una política. Una exploración insuficiente puede impedir que los valores
Q se desarrollen de manera consistente, mientras que una exploración excesiva dificulta que la política aprendida se
imponga sobre las acciones exploratorias. En un intervalo intermedio se produce la mayor concentración en el
comportamiento no cooperativo.

## 4.6. E4: efecto de la profundidad del vecindario

E4 analiza qué ocurre cuando los agentes disponen de información correspondiente a vecindarios de diferente profundidad.

El resultado vuelve a mostrar que ampliar la información disponible no conduce a la cooperación. El estado $
(1,1,0,0)$ continúa siendo el principal estado visitado, pero su frecuencia aumenta al ampliar $\rho$: pasa
aproximadamente de 0.54 con $\rho=1$, a 0.67 con $\rho=2$ y a 0.71 con $\rho=4$.

La principal diferencia respecto de $\rho=1$ es, por tanto, una mayor concentración del comportamiento. Con información
restringida, las visitas permanecen distribuidas entre un conjunto más amplio de estados. Al incorporar información
procedente de distancias mayores, la dinámica se concentra progresivamente alrededor del estado dominante.

También resulta relevante que algunos estados secundarios presenten valores de $\Delta Q$ considerablemente más
negativos con $\rho=4$. Sin embargo, estos estados son poco frecuentes y, por lo tanto, su influencia sobre el
comportamiento colectivo es limitada.

En conjunto, E4 sugiere que disponer de una visión más amplia de la red refuerza la convergencia hacia la política no
cooperativa en lugar de favorecer la coordinación cooperativa.

## 4.7. E5: efecto de la representación del estado

E5 presenta una diferencia importante respecto de los experimentos anteriores porque modifica directamente la cantidad
de información que el agente utiliza para distinguir situaciones.

El resultado más evidente es que una representación más simple produce una concentración mucho mayor en un único estado.
Con S1, el estado dominante alcanza aproximadamente el 98 % de las visitas al final de la simulación. Esta proporción
disminuye progresivamente al incorporar información adicional: aproximadamente 86 % con S12, 75 % con S123 y 52 % con
S1234.

Por lo tanto, aumentar la riqueza de la representación permite distinguir más situaciones y distribuye el aprendizaje
entre un número mayor de estados. Esto reduce la concentración en un único atractor y permite observar diferencias más
específicas entre contextos.

No obstante, esta mayor capacidad de diferenciación no se traduce en cooperación. Incluso con la representación
completa, el estado $ (1,1,0,0)$ continúa siendo el más visitado y presenta una preferencia por la deserción.

E5 muestra así que la representación del estado afecta principalmente la granularidad del aprendizaje. Una
representación más rica permite distinguir contextos que una representación simple agrupa, pero la información adicional
considerada en este modelo no resulta suficiente para producir una política cooperativa estable.

## 4.8. Comparación transversal de los experimentos

Considerados conjuntamente, los experimentos permiten distinguir dos tipos de efectos.

Por un lado, la topología de la red presenta una influencia relativamente pequeña sobre el resultado global. Las tres
topologías estudiadas producen prácticamente la misma tendencia hacia la deserción y una concentración similar en el
estado dominante.

Por otro lado, los parámetros relacionados con el proceso de aprendizaje producen diferencias más visibles en la
dinámica. La tasa de aprendizaje, el nivel de exploración, la profundidad del vecindario y la representación del estado
modifican la velocidad o el grado de concentración del sistema.

Sin embargo, ninguna de estas modificaciones cambia el signo general de la preferencia aprendida. Los estados que
concentran una parte significativa de las visitas presentan valores de $\Delta Q$ negativos. De esta manera, los cambios
experimentales afectan principalmente a cómo se alcanza la política no cooperativa, pero no consiguen reemplazarla por
una política cooperativa.

Un patrón particularmente importante es la aparición recurrente del estado

$$
(1,1,0,0).
$$

Este estado representa una situación en la que el vecindario presentó una acción mayoritariamente cooperativa, el agente
había cooperado en la ronda anterior y, sin embargo, tanto la tasa de cooperación observada como la recompensa reciente
se encuentran en niveles bajos. En prácticamente todos los experimentos en los que se utiliza la representación
completa, este estado termina concentrando una parte importante de las visitas.

Su importancia no deriva únicamente de presentar un $\Delta Q$ negativo, sino de la combinación entre una preferencia
por la deserción y una frecuencia elevada. El producto

$$
P (s)=\Delta Q (s)F (s)
$$

permite identificar precisamente este tipo de situaciones. Un estado puede presentar una fuerte preferencia por desertar
y tener poca relevancia global si casi nunca es visitado. En cambio, un estado como $ (1,1,0,0)$ combina ambas
características y, por ello, constituye el principal foco del aprendizaje observado.

Otro patrón transversal es la escasa presencia de estados asociados con niveles altos de cooperación o recompensa. Las
regiones correspondientes a valores elevados de $s_3$ y $s_4$ prácticamente no son visitadas en las configuraciones
analizadas. Esto limita la posibilidad de que los agentes acumulen experiencias suficientes en situaciones de
cooperación sostenida.

Este resultado proporciona una conexión entre el comportamiento colectivo y el análisis interno del aprendizaje. La
población no solamente termina desertando: las trayectorias de los agentes se concentran progresivamente en situaciones
caracterizadas por bajos niveles de cooperación y recompensa, y en esas situaciones los valores Q favorecen la
deserción.

## 4.9. Interpretación en relación con el problema de la cooperación

Los resultados deben interpretarse considerando la diferencia entre el modelo utilizado y los mecanismos de cooperación
estudiados en trabajos clásicos sobre el IPD.

Axelrod mostró que la cooperación puede mantenerse en determinados escenarios del IPD iterado mediante mecanismos de
reciprocidad. Una estrategia como TIT FOR TAT puede utilizar explícitamente la acción anterior del oponente y responder
a ella. Además, bajo determinadas condiciones sobre la importancia de las interacciones futuras, una estrategia
cooperativa puede resultar estable.

En QOOPERATE, los agentes utilizan una representación agregada de su vecindario y aprenden mediante Q-Learning mientras
los demás agentes también modifican sus políticas. No se implementa una estrategia explícita de reciprocidad individual
ni se conserva una historia completa de las interacciones con cada vecino.

Esta diferencia proporciona un contexto importante para interpretar la persistencia de la deserción. El sistema
estudiado no dispone exactamente de los mismos mecanismos que permitieron a las estrategias cooperativas analizadas por
Axelrod aprovechar la repetición del juego.

Además, el carácter multiagente del aprendizaje introduce una dificultad adicional: cada agente modifica continuamente
el entorno de aprendizaje de los demás. Por ello, el resultado observado no debe interpretarse simplemente como la
aplicación de Q-Learning a un problema estacionario. La dinámica conjunta de las políticas puede conducir a una
situación en la que la experiencia acumulada refuerza progresivamente la deserción.

En este sentido, el resultado principal de los experimentos no es que ninguno de los parámetros estudiados tenga efecto,
sino que sus efectos se manifiestan principalmente sobre la dinámica de aprendizaje y no sobre el comportamiento
cualitativo final. La cooperación no emerge de manera estable bajo las representaciones, estructuras de interacción y
parámetros considerados.

## 4.10. Síntesis de los resultados

Los cinco experimentos pueden resumirse de la siguiente manera:

| Experimento | Variable estudiada        | Efecto principal observado                                 | Resultado colectivo |
|-------------|---------------------------|------------------------------------------------------------|---------------------|
| E1          | Topología                 | Diferencias pequeñas en la dinámica                        | No cooperación      |
| E2          | $\alpha$                  | Modifica la velocidad y concentración del aprendizaje      | No cooperación      |
| E3          | $\epsilon$                | Regula exploración y consolidación de la política          | No cooperación      |
| E4          | $\rho$                    | Mayor profundidad aumenta la concentración                 | No cooperación      |
| E5          | Representación del estado | Mayor información distribuye las visitas entre más estados | No cooperación      |

En consecuencia, el resultado experimental más robusto es la persistencia de la deserción frente a las variaciones
estudiadas. Las diferencias entre experimentos aparecen principalmente en la trayectoria seguida para alcanzar este
comportamiento y en la estructura interna de los estados visitados y valores Q aprendidos.

Este resultado justifica la segunda etapa del trabajo: cuando la variación de los parámetros no produce cooperación,
resulta más informativo estudiar qué estados terminan dominando el proceso y qué preferencias aprenden los agentes en
ellos. El análisis de $\Delta Q$, $F$ y $P$ permite pasar, de esta manera, de una descripción del comportamiento
observable a una caracterización del proceso de aprendizaje que lo genera.

# 5. Conclusiones finales

El presente trabajo estudió el comportamiento de agentes que participan en el Dilema del Prisionero Iterado sobre una
red y aprenden sus decisiones mediante Q-Learning. El objetivo inicial consistió en analizar bajo qué condiciones podían
emerger comportamientos cooperativos o no cooperativos, considerando tanto las características de la red como diferentes
aspectos del proceso de aprendizaje.

Los resultados obtenidos muestran una tendencia consistente hacia la no cooperación en todas las configuraciones
estudiadas. La modificación de la topología de la red, de la tasa de aprendizaje, del nivel de exploración, de la
profundidad del vecindario y de la representación del estado no produjo una transición sostenida hacia un comportamiento
cooperativo. Esto constituye el resultado más robusto del estudio.

Sin embargo, los experimentos también muestran que los parámetros analizados sí afectan la dinámica mediante la cual se
alcanza este resultado. La tasa de aprendizaje y el nivel de exploración modifican principalmente la velocidad y el
grado de consolidación de la política aprendida. La profundidad del vecindario tiende a incrementar la concentración de
las visitas en un estado dominante, mientras que una representación del estado más detallada distribuye el aprendizaje
entre una cantidad mayor de estados. En cambio, las diferencias entre las tres topologías estudiadas resultaron
relativamente pequeñas.

El análisis de los valores Q permitió profundizar esta observación. La mayoría de los estados visitados con frecuencia
presentan

$$
\Delta Q (s)=Q (s,C)-Q (s,D)<0,
$$

lo que indica una preferencia aprendida por la deserción. Además, la frecuencia de visitas muestra que, a medida que
avanza el aprendizaje, los agentes tienden a concentrarse en un conjunto reducido de situaciones.

En particular, el estado $ (1,1,0,0)$ aparece recurrentemente como el principal estado visitado en las configuraciones
que utilizan la representación completa. Su importancia no se debe únicamente a que presente una diferencia de valores Q
favorable a la deserción, sino también a que concentra una proporción considerable de las visitas. La combinación de
ambas características queda reflejada mediante la medida

$$
P (s)=\Delta Q (s)F (s),
$$

que permite identificar estados que poseen simultáneamente una preferencia aprendida significativa y una elevada
presencia en la dinámica del sistema.

Un resultado adicional es la escasa presencia de estados asociados con niveles elevados de cooperación y recompensa. En
particular, los estados correspondientes a niveles altos de las variables de cooperación vecinal y recompensa reciente
prácticamente no forman parte de las trayectorias finales de los agentes. Esto sugiere que el sistema dispone de pocas
experiencias sostenidas en situaciones que podrían servir como base para el aprendizaje de una política cooperativa.

La comparación con los resultados clásicos de Axelrod permite contextualizar esta observación. En sus experimentos con
el Dilema del Prisionero Iterado, determinadas estrategias basadas en reciprocidad, como TIT FOR TAT, pueden mantener la
cooperación bajo determinadas condiciones. El modelo estudiado en este trabajo presenta diferencias importantes: los
agentes no utilizan estrategias explícitas de reciprocidad, sino que aprenden mediante Q-Learning a partir de una
representación agregada de su vecindario, mientras que todos los agentes modifican simultáneamente sus políticas.

Por este motivo, los resultados no permiten concluir que la cooperación sea imposible en el Dilema del Prisionero
Iterado ni que Q-Learning sea incapaz de producirla. La conclusión es más específica: bajo las representaciones de
estado, estructuras de red, parámetros de aprendizaje y horizonte temporal utilizados en QOOPERATE, no se observó una
emergencia estable de cooperación.

Esta distinción también delimita el alcance de los resultados. La ausencia de cooperación puede depender de
características concretas del modelo, como la representación agregada del vecindario, la ausencia de identificación
individual de los oponentes, la discretización de las variables de estado o la dinámica simultánea de aprendizaje. Por
lo tanto, modificar estos componentes constituye una posible vía para determinar si la cooperación puede emerger bajo
condiciones diferentes.

La segunda etapa del trabajo resultó relevante precisamente por esta razón. Ante la similitud de los resultados
colectivos obtenidos al variar los parámetros, el análisis de $\Delta Q$ y de la frecuencia de visitas permitió estudiar
no solamente qué comportamiento aparece, sino también cómo se construye dicho comportamiento durante el aprendizaje.
Esta perspectiva mostró que la convergencia hacia la deserción está acompañada por una progresiva concentración de la
experiencia en estados donde la deserción posee mayor valor aprendido.

En términos generales, el trabajo muestra que la dinámica de un sistema multiagente no puede caracterizarse únicamente a
partir de su resultado final. Dos configuraciones pueden alcanzar un comportamiento colectivo similar mediante procesos
de aprendizaje diferentes. El análisis conjunto del comportamiento observable y de los valores internos del agente
permite distinguir estas situaciones y proporciona una descripción más completa de la dinámica emergente.

Como continuación natural del trabajo, sería posible estudiar representaciones que conserven información individual
sobre los vecinos, incorporar memoria explícita de interacciones anteriores o modificar el mecanismo mediante el cual
los agentes reciben y utilizan información sobre sus oponentes. También sería de interés analizar configuraciones
adicionales del factor de descuento, diferentes esquemas de exploración y otros algoritmos de aprendizaje multiagente.
Estas extensiones permitirían determinar si la persistencia de la deserción observada corresponde principalmente a las
características del problema del Dilema del Prisionero o a las restricciones introducidas por el modelo de aprendizaje y
representación utilizado.

En conclusión, los experimentos realizados muestran una marcada robustez de la no cooperación bajo las condiciones
estudiadas. Las distintas configuraciones modifican la velocidad, concentración y estructura interna del aprendizaje,
pero ninguna logra establecer cooperación de manera sostenida. El análisis de los valores Q y de los estados visitados
permite explicar este resultado con mayor profundidad y constituye una base para estudiar, en trabajos posteriores, qué
modificaciones del modelo serían necesarias para favorecer la aparición de mecanismos de cooperación.

