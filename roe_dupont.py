"""
Simulador ROE - Modelo DuPont
=============================
Funcionalidad 1: Cálculo de ratios financieros básicos.

A partir de cuatro variables contables capturadas con sliders (utilidad neta,
ventas, activos promedio y patrimonio promedio), la aplicación calcula:

    Margen neto              = Utilidad neta / Ventas
    Rotación de activos      = Ventas / Activos promedio
    Apalancamiento financiero = Activos promedio / Patrimonio promedio

    ROE = Margen neto x Rotación de activos x Apalancamiento financiero
        = Utilidad neta / Patrimonio promedio

Ejecución (con el entorno virtual activo):
    streamlit run roe_dupont.py

Bibliotecas utilizadas: streamlit, pandas.
"""

from dataclasses import dataclass

import pandas as pd
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
