# Documento de Funcionalidades del Proyecto

Este documento describe las funcionalidades que desarrollaremos en el proyecto **ROE DuPont Interactivo**, utilizando **Cursor AI** como entorno de desarrollo.  

El enfoque que seguimos es **pedagógico**: queremos ilustrar cómo un proyecto puede dividirse en distintas etapas (*sprints*), cada una con un entregable funcional. En un entorno real, muchas de estas funcionalidades podrían desarrollarse de forma iterativa o integrada, pero aquí las mantendremos separadas para fines de enseñanza.

---

## Funcionalidad 1: Cálculo de ratios financieros básicos

**Objetivo**: Capturar las variables contables clave y calcular los componentes del modelo DuPont.  

**Alcance**:
- Entrada mediante *sliders* de 4 variables:  
  - Utilidad Neta  
  - Ventas  
  - Activos Promedio  
  - Patrimonio Promedio  
- Cálculo de los tres componentes:  
  - Margen Neto  
  - Rotación de Activos  
  - Apalancamiento Financiero  
- Estimación del **ROE (Return on Equity)** como producto de los tres factores.  
- Visualización de resultados en métricas numéricas.

---

## Funcionalidad 2: Visualización 3D del Prisma ROE

**Objetivo**: Representar gráficamente la descomposición del ROE.  

**Alcance**:
- Construcción de un prisma tridimensional que muestre la interacción de:  
  - Margen Neto  
  - Rotación de Activos  
  - Apalancamiento Financiero  
- El prisma deberá actualizarse dinámicamente cuando cambien las variables de entrada.  
- Etiquetas y ejes explicativos que refuercen la interpretación del modelo DuPont.  

Esta es la **“joya pedagógica”** del proyecto: permite comprender de forma intuitiva cómo se combinan los factores para determinar el ROE.

---

## Funcionalidad 3: Estados Financieros Simplificados

**Objetivo**: Complementar el análisis con un contexto contable básico.  

**Alcance**:
- Generación de un **Estado de Resultados simplificado**, con ventas, gastos y utilidad neta.  
- Generación de un **Balance General simplificado**, mostrando activos, deuda y patrimonio.  
- Visualizaciones en gráficos de barras para resaltar la coherencia entre inputs y resultados.  

---

## Nota final

Estas funcionalidades se desarrollarán **en tres sprints**, cada uno enfocado en una parte específica del proyecto.  
Al mantenerlas separadas, los estudiantes podrán comprender mejor cómo se construye progresivamente un sistema, desde los cálculos básicos hasta las visualizaciones avanzadas y el contexto financiero.  

Este enfoque permite practicar no solo la programación con **Python, Streamlit y Plotly**, sino también la organización profesional de un proyecto de desarrollo con **Cursor AI**.
