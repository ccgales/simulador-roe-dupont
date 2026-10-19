"""
Simulador ROE - Modelo DuPont
=============================
Funcionalidad 1: Cálculo de ratios financieros básicos.
Funcionalidad 2: Visualización 3D del prisma ROE (Plotly).

A partir de cuatro variables contables capturadas con sliders (utilidad neta,
ventas, activos promedio y patrimonio promedio), la aplicación calcula:

    Margen neto              = Utilidad neta / Ventas
    Rotación de activos      = Ventas / Activos promedio
    Apalancamiento financiero = Activos promedio / Patrimonio promedio

    ROE = Margen neto x Rotación de activos x Apalancamiento financiero
        = Utilidad neta / Patrimonio promedio

Ejecución (con el entorno virtual activo):
    streamlit run roe_dupont.py

El prisma 3D representa los tres componentes como las aristas de un
paralelepípedo (ancho = margen neto, largo = rotación, alto = apalancamiento).
Su volumen es el ROE: con el margen expresado en puntos porcentuales,
volumen = margen (%) x rotación x apalancamiento = ROE (%).

Bibliotecas utilizadas: streamlit, pandas, plotly.
"""

from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# 1. LÓGICA FINANCIERA (funciones puras, sin dependencias de Streamlit)
#    Se mantienen separadas de la interfaz para poder probarlas y reutilizarlas
#    en las funcionalidades posteriores (prisma 3D y estados financieros).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResultadoDuPont:
    """Contenedor inmutable con los componentes del modelo DuPont y el ROE."""

    margen_neto: float  # Utilidad neta / Ventas
    rotacion_activos: float  # Ventas / Activos promedio (veces)
    apalancamiento: float  # Activos promedio / Patrimonio promedio (veces)
    roe: float  # Producto de los tres componentes
    roe_directo: float  # Utilidad neta / Patrimonio (control de coherencia)


def _dividir(numerador: float, denominador: float) -> float:
    """División segura: devuelve 0.0 si el denominador es cero."""
    return numerador / denominador if denominador != 0 else 0.0


def calcular_dupont(
    utilidad_neta: float,
    ventas: float,
    activos_promedio: float,
    patrimonio_promedio: float,
) -> ResultadoDuPont:
    """Calcula los tres componentes DuPont y el ROE.

    Parámetros (todos en la misma unidad monetaria, por ejemplo millones):
        utilidad_neta: resultado del ejercicio después de impuestos.
        ventas: ingresos operacionales del período.
        activos_promedio: promedio de los activos totales del período.
        patrimonio_promedio: promedio del patrimonio del período.
    """
    margen_neto = _dividir(utilidad_neta, ventas)
    rotacion_activos = _dividir(ventas, activos_promedio)
    apalancamiento = _dividir(activos_promedio, patrimonio_promedio)

    # El ROE DuPont es el producto de los tres factores.
    roe = margen_neto * rotacion_activos * apalancamiento

    # Cálculo directo para verificar que la descomposición es consistente.
    roe_directo = _dividir(utilidad_neta, patrimonio_promedio)

    return ResultadoDuPont(
        margen_neto=margen_neto,
        rotacion_activos=rotacion_activos,
        apalancamiento=apalancamiento,
        roe=roe,
        roe_directo=roe_directo,
    )


# --- Visualización: prisma 3D del ROE ---------------------------------------

# Colores asociados a cada componente (se reutilizan en aristas y leyenda).
COLOR_MARGEN = "#2E7D32"  # verde
COLOR_ROTACION = "#EF6C00"  # naranja
COLOR_APALANCAMIENTO = "#6A1B9A"  # morado

# Techos mínimos de cada eje: mantienen una escala estable al mover los sliders,
# de modo que el cambio de tamaño del prisma sea visible. Si un valor los
# supera, el eje se amplía automáticamente.
TECHO_MARGEN_PCT = 20.0
TECHO_ROTACION = 3.0
TECHO_APALANCAMIENTO = 6.0


def _rango_eje(valor: float, techo: float) -> list[float]:
    """Rango [mínimo, máximo] de un eje con holgura del 15 % sobre el valor.

    Incluye siempre el cero; si el valor es negativo (p. ej. margen en caso de
    pérdida) el eje se extiende hacia el lado negativo.
    """
    holgura = valor * 1.15
    return [min(0.0, holgura), max(techo, holgura)]


def crear_figura_prisma(resultado: ResultadoDuPont) -> go.Figure:
    """Construye el prisma 3D del ROE a partir de los componentes DuPont.

    Las tres aristas que parten del origen miden:
        eje X -> margen neto (en puntos porcentuales)
        eje Y -> rotación de activos (veces)
        eje Z -> apalancamiento financiero (veces)

    El volumen del prisma (X * Y * Z) equivale al ROE expresado en %.
    """
    # Dimensiones del prisma. El margen se pasa a puntos porcentuales para que
    # el volumen resultante sea directamente el ROE en %.
    x = resultado.margen_neto * 100
    y = resultado.rotacion_activos
    z = resultado.apalancamiento

    # Un ROE negativo (pérdida) se resalta en rojo; el positivo en azul.
    color_prisma = "#1565C0" if resultado.roe >= 0 else "#C62828"

    # Los 8 vértices del paralelepípedo. Índice = bit_x + 2*bit_y + 4*bit_z.
    vx = [0, x, 0, x, 0, x, 0, x]
    vy = [0, 0, y, y, 0, 0, y, y]
    vz = [0, 0, 0, 0, z, z, z, z]

    # Caras del prisma: 6 caras x 2 triángulos, referenciadas por vértice.
    triangulos = [
        (0, 1, 3), (0, 3, 2),  # base inferior (z = 0)
        (4, 5, 7), (4, 7, 6),  # base superior (z = alto)
        (0, 1, 5), (0, 5, 4),  # cara frontal (y = 0)
        (2, 3, 7), (2, 7, 6),  # cara posterior (y = largo)
        (0, 2, 6), (0, 6, 4),  # cara izquierda (x = 0)
        (1, 3, 7), (1, 7, 5),  # cara derecha (x = ancho)
    ]
    caras = go.Mesh3d(
        x=vx,
        y=vy,
        z=vz,
        i=[t[0] for t in triangulos],
        j=[t[1] for t in triangulos],
        k=[t[2] for t in triangulos],
        color=color_prisma,
        opacity=0.30,
        flatshading=True,
        hoverinfo="skip",
        showlegend=False,
    )

    # Contorno del prisma: las 12 aristas dibujadas como una sola línea
    # (None separa los segmentos).
    aristas = [
        (0, 1), (2, 3), (4, 5), (6, 7),  # paralelas al eje X
        (0, 2), (1, 3), (4, 6), (5, 7),  # paralelas al eje Y
        (0, 4), (1, 5), (2, 6), (3, 7),  # paralelas al eje Z
    ]
    ex, ey, ez = [], [], []
    for a, b in aristas:
        ex += [vx[a], vx[b], None]
        ey += [vy[a], vy[b], None]
        ez += [vz[a], vz[b], None]
    contorno = go.Scatter3d(
        x=ex,
        y=ey,
        z=ez,
        mode="lines",
        line={"color": color_prisma, "width": 3},
        hoverinfo="skip",
        showlegend=False,
    )

    def arista_componente(nombre, texto, color, xs, ys, zs):
        """Arista destacada que parte del origen, con la medida del componente."""
        return go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="lines+text",
            name=nombre,
            line={"color": color, "width": 9},
            text=["", texto, ""],
            textposition="top center",
            textfont={"color": color, "size": 13},
            hovertemplate=f"{nombre}: {texto}<extra></extra>",
        )

    # Las tres aristas que parten del origen representan cada componente DuPont.
    arista_x = arista_componente(
        "Margen neto",
        f"{x:.2f}%",
        COLOR_MARGEN,
        [0, x / 2, x],
        [0, 0, 0],
        [0, 0, 0],
    )
    arista_y = arista_componente(
        "Rotación de activos",
        f"{y:.2f}x",
        COLOR_ROTACION,
        [0, 0, 0],
        [0, y / 2, y],
        [0, 0, 0],
    )
    arista_z = arista_componente(
        "Apalancamiento financiero",
        f"{z:.2f}x",
        COLOR_APALANCAMIENTO,
        [0, 0, 0],
        [0, 0, 0],
        [0, z / 2, z],
    )

    # Etiqueta con el ROE en el centro del prisma (su volumen).
    centro = go.Scatter3d(
        x=[x / 2],
        y=[y / 2],
        z=[z / 2],
        mode="text",
        text=[f"ROE<br>{resultado.roe:.2%}"],
        textfont={"color": color_prisma, "size": 16},
        hoverinfo="skip",
        showlegend=False,
    )

    figura = go.Figure(data=[caras, contorno, arista_x, arista_y, arista_z, centro])
    figura.update_layout(
        title={
            "text": (
                "Prisma financiero DuPont: el volumen es el ROE<br>"
                f"<sup>{x:.2f}% (margen) x {y:.2f} (rotación) x {z:.2f} "
                f"(apalancamiento) = {resultado.roe:.2%}</sup>"
            ),
            "x": 0.5,
        },
        scene={
            "xaxis": {
                "title": {"text": "Margen neto (%)"},
                "range": _rango_eje(x, TECHO_MARGEN_PCT),
            },
            "yaxis": {
                "title": {"text": "Rotación de activos (veces)"},
                "range": _rango_eje(y, TECHO_ROTACION),
            },
            "zaxis": {
                "title": {"text": "Apalancamiento (veces)"},
                "range": _rango_eje(z, TECHO_APALANCAMIENTO),
            },
            "aspectmode": "cube",
            "camera": {"eye": {"x": 1.6, "y": 1.6, "z": 0.9}},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.05,
            "xanchor": "center",
            "x": 0.5,
        },
        margin={"l": 0, "r": 0, "t": 80, "b": 0},
        height=620,
    )
    return figura


# ---------------------------------------------------------------------------
# 2. CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Simulador ROE DuPont",
    page_icon=":material/analytics:",
    layout="wide",
)

st.title("Simulador ROE - Modelo DuPont")
st.caption(
    "Descomposición del retorno sobre el patrimonio (ROE) en margen neto, "
    "rotación de activos y apalancamiento financiero."
)

# ---------------------------------------------------------------------------
# 3. ENTRADA DE DATOS (sliders en la barra lateral)
#    Valores por defecto coherentes: margen 8 %, rotación 1,25x,
#    apalancamiento 2,0x  ->  ROE = 20 %.
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Variables contables")
    st.caption("Cifras en millones de la moneda de reporte.")

    utilidad_neta = st.slider(
        "Utilidad neta",
        min_value=-500,
        max_value=5_000,
        value=160,
        step=10,
        help="Resultado del ejercicio después de impuestos. Puede ser negativa (pérdida).",
    )
    ventas = st.slider(
        "Ventas",
        min_value=100,
        max_value=20_000,
        value=2_000,
        step=50,
        help="Ingresos operacionales del período.",
    )
    activos_promedio = st.slider(
        "Activos promedio",
        min_value=100,
        max_value=20_000,
        value=1_600,
        step=50,
        help="Promedio de los activos totales entre el inicio y el cierre del período.",
    )
    patrimonio_promedio = st.slider(
        "Patrimonio promedio",
        min_value=50,
        max_value=10_000,
        value=800,
        step=50,
        help="Promedio del patrimonio entre el inicio y el cierre del período.",
    )

# ---------------------------------------------------------------------------
# 4. CÁLCULO
# ---------------------------------------------------------------------------

resultado = calcular_dupont(
    utilidad_neta=utilidad_neta,
    ventas=ventas,
    activos_promedio=activos_promedio,
    patrimonio_promedio=patrimonio_promedio,
)

# ---------------------------------------------------------------------------
# 5. RESULTADOS
# ---------------------------------------------------------------------------

# Alerta de coherencia contable: Activos = Pasivos + Patrimonio, por lo que el
# patrimonio no debería superar a los activos (apalancamiento < 1).
if patrimonio_promedio > activos_promedio:
    st.warning(
        "El patrimonio promedio supera a los activos promedio, lo que implica "
        "un apalancamiento menor a 1,0x y no es coherente con la ecuación "
        "contable (Activos = Pasivos + Patrimonio). Revise los valores.",
        title="Datos inconsistentes",
    )

st.subheader("Retorno sobre el patrimonio (ROE)")
st.metric(
    "ROE",
    f"{resultado.roe:.2%}",
    help="ROE = Margen neto x Rotación de activos x Apalancamiento financiero.",
    border=True,
)

st.subheader("Componentes del modelo DuPont")
with st.container(horizontal=True):
    st.metric(
        "Margen neto",
        f"{resultado.margen_neto:.2%}",
        help="Utilidad neta / Ventas. Mide la rentabilidad de cada unidad vendida.",
        border=True,
    )
    st.metric(
        "Rotación de activos",
        f"{resultado.rotacion_activos:.2f}x",
        help="Ventas / Activos promedio. Mide la eficiencia en el uso de los activos.",
        border=True,
    )
    st.metric(
        "Apalancamiento financiero",
        f"{resultado.apalancamiento:.2f}x",
        help="Activos promedio / Patrimonio promedio. Mide cuánto del activo se financia con patrimonio ajeno.",
        border=True,
    )

# Prisma 3D: se reconstruye en cada cambio de los sliders, por lo que el
# gráfico siempre refleja las variables de entrada actuales.
st.subheader("Prisma ROE en 3D")
with st.container(border=True):
    st.plotly_chart(
        crear_figura_prisma(resultado),
        width="stretch",
        alt="Prisma 3D del modelo DuPont: margen neto, rotación de activos y apalancamiento financiero, cuyo volumen equivale al ROE",
    )
    st.markdown(
        "**Cómo interpretarlo:** cada arista del prisma es un componente del "
        "modelo DuPont y su volumen equivale al ROE. Para aumentar el ROE se "
        "puede ampliar cualquiera de las tres dimensiones:\n"
        "- **Margen neto (verde):** mejorar la rentabilidad de cada venta.\n"
        "- **Rotación de activos (naranja):** vender más con los mismos activos.\n"
        "- **Apalancamiento (morado):** financiar más activos con deuda; "
        "aumenta el ROE, pero también el riesgo financiero.\n\n"
        "Una pérdida (margen negativo) invierte el prisma hacia el lado "
        "negativo del eje y lo muestra en rojo."
    )

# Detalle del cálculo: útil en clase para seguir la fórmula paso a paso.
st.subheader("Detalle del cálculo")
st.latex(
    r"ROE = \underbrace{\frac{\text{Utilidad neta}}{\text{Ventas}}}_{\text{Margen neto}}"
    r"\times \underbrace{\frac{\text{Ventas}}{\text{Activos}}}_{\text{Rotación}}"
    r"\times \underbrace{\frac{\text{Activos}}{\text{Patrimonio}}}_{\text{Apalancamiento}}"
)

detalle = pd.DataFrame(
    {
        "Indicador": [
            "Margen neto",
            "Rotación de activos",
            "Apalancamiento financiero",
            "ROE (producto de los tres)",
        ],
        "Fórmula": [
            f"{utilidad_neta:,.0f} / {ventas:,.0f}",
            f"{ventas:,.0f} / {activos_promedio:,.0f}",
            f"{activos_promedio:,.0f} / {patrimonio_promedio:,.0f}",
            "Margen x Rotación x Apalancamiento",
        ],
        "Resultado": [
            f"{resultado.margen_neto:.2%}",
            f"{resultado.rotacion_activos:.2f}x",
            f"{resultado.apalancamiento:.2f}x",
            f"{resultado.roe:.2%}",
        ],
    }
)
st.dataframe(detalle, hide_index=True, alt="Detalle del cálculo del ROE por el modelo DuPont")

# Verificación: el producto DuPont debe coincidir con Utilidad neta / Patrimonio.
st.caption(
    f"Verificación: Utilidad neta / Patrimonio promedio = {resultado.roe_directo:.2%} "
    f"(coincide con el ROE calculado por la descomposición DuPont)."
)
