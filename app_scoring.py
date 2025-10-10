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

    
    
    def etiqueta_generica(v: float):
        if v < 40:  return "Negativo"
        if v <= 60: return "Neutral"
        return "Positivo"

    def gauge_options(valor: float, title_label: str, label_fn=etiqueta_generica):
        v = max(0, min(100, float(valor)))
        etiqueta = label_fn(v)
        return {
            "backgroundColor": "#1f2630",
            "series": [{
                "type": "gauge",
                "startAngle": 210, "endAngle": -30,
                "min": 0, "max": 100, "splitNumber": 6,
                "center": ["50%", "60%"], "radius": "90%",

                # Arco por segmentos (rojo-ámbar-verde)
                "axisLine": {"roundCap": True, "lineStyle": {
                    "width": 22,
                    "color": [[0.33, "#d84343"], [0.66, "#f1c232"], [1.0, "#3ecf8e"]],
                }},
                # Huecos entre segmentos (mismo color que el fondo)
                "splitLine": {
                    "distance": -22, "length": 12,
                    "lineStyle": {"width": 10, "color": "#1f2630"}
                },
                "axisTick": {"show": False}, "axisLabel": {"show": False},

                # Progreso y aguja
                "progress": {"show": True, "roundCap": True, "width": 22, "itemStyle": {"color": "#ffffff22"}},
                "pointer": {"show": True, "length": "72%", "width": 6, "itemStyle": {"color": "#ffffff"}},
                "anchor": {"show": True, "size": 10, "itemStyle": {"color": "#ffffff", "shadowColor": "#00000055", "shadowBlur": 8}},

                # Título (nombre del gauge) y número central
                "title": {"show": True, "offsetCenter": [0, "20%"], "color": "#dfe6ee", "fontSize": 18, "fontWeight": 600},
                "detail": {"valueAnimation": True, "formatter": "{value}", "color": "#ffffff", "fontSize": 44, "offsetCenter": [0, "-2%"]},

                "data": [{"value": v, "name": f"{title_label} · {etiqueta}"}],
            }],
            "animationDuration": 600, "animationEasing": "cubicOut",
        }

    # ---------- Inputs (ejemplo: sliders; sustituye por tus KPIs) ----------
    #st.sidebar.header("Valores de ejemplo")
    #kpi_pd  = st.sidebar.slider("PD",  0, 100, 54)
    #kpi_ead = st.sidebar.slider("EAD", 0, 100, 72)
    #kpi_lgd = st.sidebar.slider("LGD", 0, 100, 35)

    # ---------- Render ----------
    st.markdown("### Indicadores de Riesgo")
    c1, c2, c3 = st.columns(3)

    with c1:
        st_echarts(gauge_options(kpi_pd,  "PD"),  height="300px", key="gauge_pd")
    with c2:
        st_echarts(gauge_options(kpi_ead, "EAD"), height="300px", key="gauge_ead")
    with c3:
        st_echarts(gauge_options(kpi_lgd, "LGD"), height="300px", key="gauge_lgd")
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





