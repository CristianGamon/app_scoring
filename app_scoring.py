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

    def build_meter_options(value, name, maximum=100):
    
        # Normaliza valor a 0–maximum
        v = float(value)
        if 0 <= v <= 1:
            v = v * maximum
        v = max(0, min(maximum, v))
        prop = v / maximum  # 0–1
        
        options = {
            "grid": {"left": 20, "right": 20, "bottom": 20, "top": 30},
            "xAxis": {"show": False, "type": "value", "max": 1},
            "yAxis": {"show": True, "type": "category", "data": [name]},
            "series": [
                # Fondo completo
                {
                    "type": "pictorialBar",
                    "symbol": "rect",
                    "symbolSize": [30, 180],
                    "symbolRepeat": False,
                    "symbolBoundingData": 1,
                    "itemStyle": {"color": "#E6E6E6", "opacity": 1},
                    "z": 1,
                    "data": [1],
                },
                # Relleno dinámico según value
                {
                    "type": "pictorialBar",
                    "symbol": "rect",
                    "symbolSize": [30, 180],
                    "symbolRepeat": False,
                    "symbolBoundingData": 1,
                    "symbolClip": True,               # <- recorte por valor
                    "itemStyle": {
                        "color": {
                            "type": "linear",
                            "x": 0, "y": 1, "x2": 0, "y2": 0,
                            "colorStops": [
                                {"offset": 0.0, "color": "#55DD55"},  # verde
                                {"offset": 0.7, "color": "#FFAA00"},  # ámbar
                                {"offset": 1.0, "color": "#FF4444"},  # rojo
                            ],
                        }
                    },
                    "label": {
                        "show": True,
                        "position": "insideTop",
                        "formatter": f"{v:.0f}",
                        "fontSize": 12,
                        "color": "black",
                    },
                    "z": 2,
                    "data": [prop],
                },
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


