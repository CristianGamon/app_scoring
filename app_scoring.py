from codigo_de_ejecucion import *
import streamlit as st
from streamlit_echarts import st_echarts

#CONFIGURACION DE LA PÁGINA
st.set_page_config(
     page_title = 'Risk Score Analyzer',
     page_icon = '⚖️',
     layout = 'wide')

#SIDEBAR
with st.sidebar:
    st.image('Perfil-crediticio.jpg')

    #INPUTS DE LA APLICACION
    principal = st.slider('Importe Solicitado', 1000, 40000)
    finalidad = st.selectbox('Finalidad Préstamo', ['debt_consolidation','credit_card','home_improvement','other','major_purchase','small_business','car','wedding','medical','moving','vacation','house','educational','renewable_energy'])
    vivienda = st.selectbox('Tipo Vivienda', ['MORTGAGE','RENT','OWN'])
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

    
    
    # Normaliza valor a 0–maximum
    v = float(value)
    if 0 <= v <= 1:
        v = v * maximum
    v = max(0, min(maximum, v))
    prop = v / maximum  # 0–1
    
    def label_from_value(v: float) -> str:
        """Etiqueta según el valor (0-100). Cambia los umbrales a tu gusto."""
        if v < 40:
            return "Negativo"
        elif v <= 60:
            return "Neutral"
        return "Positivo"

    def gauge_options(value: float):
        """
        Devuelve la configuración ECharts para un indicador semicircular
        con segmentos y valor central. value entre 0 y 100.
        """
        value = max(0, min(100, float(value)))
        options = {
            "backgroundColor": "#1f2630",  # fondo oscuro similar a la imagen
            "series": [
                {
                    "type": "gauge",
                    "startAngle": 210,     # semicircular
                    "endAngle": -30,
                    "min": 0,
                    "max": 100,
                    "splitNumber": 6,      # número de tramos
                    "center": ["50%", "60%"],
                    "radius": "90%",

                    # arco de fondo con segmentos (rojo -> ámbar -> verde)
                    "axisLine": {
                        "roundCap": True,
                        "lineStyle": {
                            "width": 22,
                            "color": [
                                [0.33, "#d84343"],  # rojo
                                [0.66, "#f1c232"],  # ámbar
                                [1.00, "#3ecf8e"],  # verde
                            ],
                        },
                    },
                    # líneas de división gruesas para simular “segmentos con hueco”
                    "splitLine": {
                        "distance": -22,
                        "length": 12,
                        "lineStyle": {"width": 10, "color": "#1f2630"}  # mismo color del fondo
                    },
                    "axisTick": {"show": False},
                    "axisLabel": {"show": False},

                    # progreso relleno (arco que avanza)
                    "progress": {
                        "show": True,
                        "roundCap": True,
                        "width": 22,
                        "itemStyle": {"color": "#ffffff22"},  # color del “relleno” encima; sutil
                    },

                    # aguja sencilla (opcional). Si no la quieres, pon "show": False
                    "pointer": {
                        "show": True,
                        "length": "72%",
                        "width": 6,
                        "itemStyle": {"color": "#ffffff"}  # blanco
                    },

                    # círculo en la punta de la aguja (truco: shadow y border)
                    "anchor": {   # ancla en el centro (estética, opcional)
                        "show": True,
                        "size": 10,
                        "itemStyle": {"color": "#ffffff", "shadowColor": "#00000055", "shadowBlur": 8}
                    },

                    # título (debajo del número)
                    "title": {
                        "show": True,
                        "offsetCenter": [0, "20%"],
                        "color": "#dfe6ee",
                        "fontSize": 22,
                        "fontWeight": "600"
                    },

                    # número grande
                    "detail": {
                        "valueAnimation": True,
                        "formatter": "{value}",
                        "color": "#ffffff",
                        "fontSize": 48,
                        "offsetCenter": [0, "-2%"],
                    },

                    "data": [{"value": value, "name": label_from_value(value)}],
                }
            ],
            "animationDuration": 600,
            "animationEasing": "cubicOut",
        }
        return options
    
    pd_options  = build_meter_options(kpi_pd,  name="pd",  maximum=100)
    ead_options = build_meter_options(kpi_ead, name="ead", maximum=100)
    lgd_options = build_meter_options(kpi_lgd, name="lgd", maximum=100)
    
    #Representarlos en la app
    col1,col2,col3 = st.columns(3)
    with col1:
        st_echarts(options=pd_options, width="110%", height="300px", key = 'meter_pd')
    with col2:
        st_echarts(options=ead_options, width="110%", height="300px", key = 'meter_ead')
    with col3:
        st_echarts(options=lgd_options, width="110%", height="300px", key = 'meter_lgd')

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



