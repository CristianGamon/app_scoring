from codigo_de_ejecucion import *
import streamlit as st
from streamlit_echarts import st_echarts

#CONFIGURACION DE LA PÁGINA
st.set_page_config(
     page_title = 'Risk Score Analyzer',
     page_icon = 'dollar',
     layout = 'wide')

#SIDEBAR
with st.sidebar:
    st.image('Perfil-crediticio.jpg')

    #INPUTS DE LA APLICACION
    principal = st.number_input('Importe Solicitado', 1000, 40000)
    finalidad = st.selectbox('Finalidad Préstamo', ['debt_consolidation','credit_card','home_improvement','other','major_purchase','small_business','car','wedding','medical','moving','vacation','house','educational','renewable_energy'])
    num_cuotas = st.radio('Número Cuotas', ['36 months','60 months'])
    ingresos = st.number_input('Ingresos anuales', 20000, 500000)

    #DATOS CONOCIDOS (fijadas como datos estaticos por simplicidad)
    ingresos_verificados = 'Verified'
    antigüedad_empleo = '10+ years'
    rating = 'B'
    dti = 28
    num_lineas_credito = 3
    porc_uso_revolving = 50
    tipo_interes = 7.26
    imp_cuota = 500
    num_derogatorios = 0
    vivienda = 'MORTGAGE'




#MAIN
st.title('RISK SCORE ANALYZER')


#CALCULAR

#Crear el registro
registro = pd.DataFrame({'ingresos_verificados':ingresos_verificados,
                         'vivienda':vivienda,
                         'finalidad':finalidad,
                         'num_cuotas':num_cuotas,
                         'antigüedad_empleo':antigüedad_empleo,
                         'rating':rating,
                         'ingresos':ingresos,
                         'dti':dti,
                         'num_lineas_credito':num_lineas_credito,
                         'porc_uso_revolving':porc_uso_revolving,
                         'principal':principal,
                         'tipo_interes':tipo_interes,
                         'imp_cuota':imp_cuota,
                         'num_derogatorios':num_derogatorios}
                        ,index=[0])



#CALCULAR RIESGO
if st.sidebar.button('CALCULAR RIESGO'):
    #Ejecutar el scoring
    EL = ejecutar_modelos(registro)

    #Calcular los kpis
    kpi_pd = int(EL.pd * 100)
    kpi_ead = int(EL.ead * 100)
    kpi_lgd = int(EL.lgd * 100)
    kpi_el = int(EL.principal * EL.pd * EL.ead * EL.lgd)

    def tramo_color_axisline():
    # Fondo segmentado: verde 0-35, naranja 35-70, rojo 70-100
         return [
             [0.50, "#2ECC71"],  # verde hasta 35%
             [0.80, "#F39C12"],  # naranja hasta 70%
             [1.00, "#E74C3C"],  # rojo hasta 100%
         ]

    #def color_progreso(valor):
    # Color del relleno según el valor actual
        # if valor < 35:
        #     return "#2C3DBEFF"  # verde
         #elif valor < 70:
         #    return "#2C3DBEFF"  # naranja
        # else:
           #  return "#2C3DBEFF"  # rojo
     #Velocimetros
    #Codigo de velocimetros tomado de https://towardsdatascience.com/5-streamlit-components-to-build-better-applications-71e0195c82d4
    def build_gauge(nombre, valor):
         v = max(0, min(100, int(valor)))
         return {
             "series": [
                 {
                     "name": nombre.upper(),
                     "type": "gauge",
                     "min": 0, "max": 100,
                     "startAngle": 180, "endAngle": 0,
                     "radius": "100%",
                     "axisLine": {
                         "lineStyle": {
                             "width": 15,
                             "color": tramo_color_axisline(),   # <-- tramos fondo
                         }
                     },
                    # === Escala visible ===
                     "splitNumber": 5,            # nº de divisiones grandes entre min/max
                     "axisLabel": {
                         "show": True,
                         "distance": 24,
                         "fontSize": 9,
                         # Muestra solo múltiplos de 20
                         "formatter": "{value}"
                     },
                     "axisTick": {
                         "show": True,
                         "length": 6,
                         "lineStyle": {"width": 2}
                     },
                     "splitLine": {
                         "show": True,
                         "length": 10,
                         "lineStyle": {"width": 3}
                     },
     
                     # Relleno que cambia de color según el valor
                     #"progress": {
                     #    "show": True,
                     #    "width": 15,
                     #    "itemStyle": {"color": color_progreso(v)},  # <-- color dinámico
                     #    "data": {"value": kpi_pd, "name": "PD"}
                     #},
     
                     "pointer": {"show": True, "length": "90%", "width": 4},
                     "detail": {
                         "valueAnimation": True,
                         "formatter": "{value}",
                         "fontSize": 18
                     },
                     "title": {"show": True, "fontSize": 12, "offsetCenter": [0, "25%"]},
                     "data": [{"value": v, "name": nombre.upper()}],
                 }
             ]
         }
   # Velocímetros con color por rango
    pd_options  = build_gauge("PD", kpi_pd)
    ead_options = build_gauge("EAD", kpi_ead)
    lgd_options = build_gauge("LGD", kpi_lgd)
     
     # Render
    col1, col2, col3 = st.columns(3)
    with col1:
        st_echarts(options=pd_options,  width="100%", height="240px", key="g_pd")
    with col2:
        st_echarts(options=ead_options, width="100%", height="240px", key="g_ead")
    with col3:
        st_echarts(options=lgd_options, width="100%", height="240px", key="g_lgd")

    #Prescripcion
    col1,col2 = st.columns(2)
    with col1:
        st.write('La pérdida esperada es de (Euros):')
        st.metric(label="PÉRDIDA ESPERADA", value = kpi_el)
    with col2:
        st.write('Se recomienda un extratipo de (Euros):')
        st.metric(label="COMISIÓN A APLICAR", value = kpi_el * 3) #Metido en estático por simplicidad

else:
    st.write('DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO')
























