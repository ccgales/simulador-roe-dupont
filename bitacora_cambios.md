# Bitácora de cambios - ROE DuPont Interactivo

Registro cronológico de los cambios del proyecto y de los aprendizajes asociados. Cada entrada indica la fecha, qué se hizo y qué se aprendió. Las entradas nuevas se agregan al final de la sección "Registro de cambios".

**Convenciones**

- Fechas en formato `AAAA-MM-DD`.
- Funcionalidades según `documentos/funcionalidades_proyecto.md`: F1 (ratios DuPont), F2 (prisma 3D) y F3 (estados financieros).
- Los commits se citan por su código corto de Git.

---

## Resumen de estado

| Funcionalidad | Rama | Commit | Estado |
|---|---|---|---|
| Configuración inicial | `main` | `5cc32ca` | Completada |
| F1 - Cálculo de ratios financieros básicos | `feature/ratios-dupont` | `73068f7` | Completada |
| F2 - Visualización 3D del prisma ROE | `feature/prisma-3D` | `fd678f4` | Completada |
| F3 - Estados financieros simplificados | `feature/estado-balance` | `42aa7f6` | Completada |
| Documentación (README y bitácora) | `documentacion-limpieza` | Pendiente | En curso |

---

## Registro de cambios

### 2026-10-17 - Configuración inicial del proyecto

**Descripción del cambio**
- Se definieron las reglas del proyecto en `.cursor/rules/reglasproyecto.mdc` (bibliotecas permitidas, estilo del código, orientación técnico-financiera).
- Se creó `.gitignore` para excluir `.venv/`, cachés de Python y secretos locales de Streamlit.
- Se definieron las dependencias en `documentos/requiriments.txt` (`streamlit`, `plotly`, `pandas`, `numpy`).
- Se planificó la división del trabajo en ramas: una rama por funcionalidad, integradas en serie F1, F2 y F3.

**Aprendizaje asociado**
- En esta versión de Cursor las reglas ya no están en un ítem "Rules" dentro de Settings; se encuentran en **Customize**. Las reglas de usuario se editan allí; las del proyecto viven en `.cursor/rules/*.mdc` y se versionan en Git.
- El entorno virtual (`.venv/`) nunca debe ir al repositorio: se ignora desde el primer commit y cada persona crea el suyo.
- Se usó el modo **Ask** para resolver dudas (dónde van las reglas, cómo dividir en ramas, cómo ignorar `.venv`) antes de pedir cambios al modo **Agent**. Aclarar primero evitó implementar sobre supuestos equivocados.
- Las funcionalidades dependen unas de otras (F2 y F3 reutilizan los cálculos de F1), por lo que conviene desarrollarlas en serie y no en paralelo para evitar conflictos de integración.

---

### 2026-10-17 - F1: Cálculo de ratios financieros básicos

**Descripción del cambio**
- Se creó `roe_dupont.py`, la aplicación Streamlit.
- Cuatro sliders para utilidad neta, ventas, activos promedio y patrimonio promedio, con valores iniciales coherentes (ROE de 20 %).
- Función `calcular_dupont()` que devuelve margen neto, rotación de activos, apalancamiento y ROE, con división segura ante denominadores en cero.
- Métricas con ayudas contextuales, fórmula en LaTeX, tabla de detalle y verificación `Utilidad neta / Patrimonio`.
- Alerta cuando el patrimonio supera a los activos.
- Se instalaron las dependencias en `.venv`, que estaba vacío.

**Aprendizaje asociado**
- Separar los cálculos de la interfaz (funciones puras) permitió reutilizarlos en F2 y F3 sin modificarlos.
- Validar la coherencia contable desde el inicio (patrimonio mayor a activos) evita resultados engañosos más adelante.
- Un entorno virtual recién creado está vacío: hay que instalar `requiriments.txt` antes de ejecutar o probar.
- Se verificó la aplicación sin abrir el navegador con el modo de pruebas de Streamlit (`AppTest`), lo que acelera la validación.

---

### 2026-10-18 - F2: Visualización 3D del prisma ROE

**Descripción del cambio**
- Nueva función `crear_figura_prisma()` con Plotly: un paralelepípedo cuyas aristas son margen neto (eje X, en %), rotación de activos (eje Y) y apalancamiento (eje Z).
- El volumen del prisma equivale al ROE; el título muestra la ecuación completa.
- Aristas de colores distintos con su valor, ROE en el centro y ejes etiquetados.
- Ejes con escala mínima estable, que se amplía si el valor la supera.
- Una pérdida se muestra en rojo y hacia el lado negativo del eje.
- Texto de interpretación bajo el gráfico.

**Aprendizaje asociado**
- Expresar el margen en puntos porcentuales hace que "volumen = ROE" se cumpla directamente y facilita la explicación en clase.
- Con ejes de escala fija el cambio de tamaño del prisma es visible al mover los sliders; con ejes automáticos el prisma siempre parecería igual.
- Hay que prever el caso de margen negativo: el prisma debe seguir siendo válido y distinguible.
- Pedir una sola funcionalidad por vez ("solo la segunda") mantuvo el alcance acotado y evitó mezclar trabajo de F3.

---

### 2026-10-20 - F3: Estados financieros simplificados

**Descripción del cambio**
- Nuevas funciones `calcular_estado_resultados()` y `calcular_balance_general()`, más sus gráficos de Plotly, en dos columnas:
  - **Estado de resultados:** barras horizontales de Ventas (celeste), Gastos (rosado) y Utilidad neta (verde suave).
  - **Balance general:** columnas apiladas de Activos (verde) frente a Patrimonio (celeste) y Deuda (rosado).
- Cálculo por diferencia: `Gastos = Ventas - Utilidad neta` y `Deuda = Activos - Patrimonio`, conectado a los mismos sliders.
- Línea de verificación bajo cada gráfico y manejo del caso con patrimonio mayor a activos (deuda en cero y aviso).

**Aprendizaje asociado**
- Derivar gastos y deuda como diferencias garantiza que las igualdades contables (`Ventas = Gastos + Utilidad neta` y `Activos = Deuda + Patrimonio`) se cumplan siempre, sin datos adicionales.
- Los estados financieros se alimentan de las mismas cuatro variables que el ROE, por lo que quedan coherentes entre sí.
- Describir con precisión los colores y la disposición de cada gráfico en la solicitud redujo las iteraciones.

---

### 2026-10-20 - F3: Ajuste del gráfico del balance general

**Descripción del cambio**
- Las dos columnas del balance quedaron **sin espacio entre ellas** (`bargap=0`), como las dos caras de un balance: Activos a la izquierda y, a la derecha, Patrimonio en la base con Deuda encima.
- No se modificó la lógica de cálculo; solo la presentación.

**Aprendizaje asociado**
- La primera versión cumplía la lógica contable pero no la intención visual: los detalles de presentación se afinan mejor en una segunda pasada con una instrucción puntual.
- Cuando el resultado del modo **Agent** no cumple lo esperado, conviene pasar a **Ask** para entender qué se hizo y por qué, y luego pedir un ajuste concreto en lugar de repetir la solicitud completa.
- Los cambios de presentación no deben tocar los cálculos: separar ambos hizo el ajuste de bajo riesgo.

---

### 2026-10-20 - Documentación: README y bitácora

**Descripción del cambio**
- Se reescribió `README.md` con descripción, características, requisitos, instalación, guía de uso, estructura, interpretación pedagógica y nota educativa.
- Se creó esta bitácora (`bitacora_cambios.md`).

**Aprendizaje asociado**
- Documentar con base en el código y los archivos reales del repositorio (versiones, rangos de los sliders, estructura) evita información desactualizada.
- El repositorio aún no tiene archivo `LICENSE`; el README describe un uso académico y educativo, y queda pendiente decidir una licencia formal.
- El archivo de dependencias se llama `requiriments.txt` (con esa ortografía) y el README lo cita tal cual; si se renombra, hay que actualizar la documentación.

---

## Aprendizajes generales

| Tema | Aprendizaje |
|---|---|
| Modos de Cursor | **Ask** sirve para consultar, planificar y diagnosticar sin modificar archivos; **Agent** para implementar. Si Agent no cumple lo pedido, volver a Ask antes de insistir. |
| Alcance | Una funcionalidad por solicitud y una rama por funcionalidad mantienen los cambios revisables. |
| Arquitectura | Cálculos como funciones puras y gráficos en funciones separadas facilitan la reutilización y la enseñanza. |
| Solicitudes | Indicar colores, disposición y reglas de cálculo en el mismo mensaje reduce las correcciones posteriores. |
| Verificación | Probar con `AppTest` y con escenarios límite (pérdida, patrimonio mayor a activos) detecta errores sin abrir el navegador. |
| Git | `.gitignore` desde el inicio; ramas por funcionalidad integradas en serie hacia `dev` y `main`. |

---

## Plantilla para nuevas entradas

```markdown
### AAAA-MM-DD - Funcionalidad o tema

**Descripción del cambio**
- Qué se modificó, en pocas líneas.

**Aprendizaje asociado**
- Qué se aprendió y cómo aplicarlo la próxima vez.
```
