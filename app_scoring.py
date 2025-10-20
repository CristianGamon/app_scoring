from codigo_de_ejecucion import *
import streamlit as st
from streamlit_echarts import st_echarts

#PAGE CONFIGURATION
st.set_page_config(
     page_title = 'CreditScore Studio',
     page_icon = 'dollar',
     layout = 'wide')

#SIDEBAR
with st.sidebar:
    st.image('Perfil-crediticio.jpg')

    #APPLICATION INPUTS
    vivienda = st.selectbox('Housing Situation', ['MORTGAGE','RENT','OWN'])
    ingresos = st.number_input('Annual Income', 20000, 500000)
    antigüedad_empleo = st.selectbox('Employment Length', ['< 1 year','1 year','2 years','3 years','4 years','5 years','6 years','7 years','8 years','9 years','10+ years','unknown'])
    principal = st.slider('Requested Amount', 500, 40000)
    finalidad = st.selectbox('Loan Purpose', ['debt_consolidation','credit_card','home_improvement','other','major_purchase','small_business','car','wedding','medical','moving','vacation','house','educational','renewable_energy'])
    num_cuotas = st.radio('Number of Installments', ['36 months','60 months'])
    

    #KNOWN DATA (set as static values for simplicity)
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
st.title('CreditScore Studio')
st.markdown("<br><br><br>", unsafe_allow_html=True)


#CALCULATE

#Create record
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



#CALCULATE RISK
if st.sidebar.button('CALCULATE RISK'):
    #Run the scoring
    EL = ejecutar_modelos(registro)

    #Calculate KPIs
    kpi_pd = int(EL.pd * 100)
    kpi_ead = int(EL.ead * 100)
    kpi_lgd = int(EL.lgd * 100)
    kpi_el = int(EL.principal * EL.pd * EL.ead * EL.lgd)

    def tramo_color_axisline():
    # Segmented background: green 0-60, orange 60-85, red 85-100
         return [
             [0.60, "#2ECC71"],  
             [0.85, "#F39C12"],  
             [1.00, "#E74C3C"],  
         ]

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
                             "color": tramo_color_axisline(),   
                         }
                     },
                    # === Visible scale ===
                     "splitNumber": 5,            
                     "axisLabel": {
                         "show": True,
                         "distance": 24,
                         "fontSize": 9,                         
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
     
                     "pointer": {"show": True, "length": "100%", "width": 4, "itemStyle":{"color":"#212228FF"}},
                     "detail": {
                         "valueAnimation": True,
                         "formatter": "{value}",
                         "fontSize": 18,                       
                     },
                     "title": {"show": True, "fontSize": 12, "offsetCenter": [0, "25%"]},
                     "data": [{"value": v, "name": nombre.upper()}],
                 }
             ]
         }
   # Gauges with color by range
    pd_options  = build_gauge("Probability Of Default", kpi_pd)
    ead_options = build_gauge("Exposure At Default", kpi_ead)
    lgd_options = build_gauge("Loss Given Default", kpi_lgd)
     
     # Render
    col1, col2, col3 = st.columns(3)
    with col1:
        st_echarts(options=pd_options,  width="100%", height="240px", key="g_pd")
    with col2:
        st_echarts(options=ead_options, width="100%", height="240px", key="g_ead")
    with col3:
        st_echarts(options=lgd_options, width="100%", height="240px", key="g_lgd")

    #Prescription
    col1,col2 = st.columns(2)
    with col1:
        st.write('The expected loss is (Euros):')
        st.metric(label="EXPECTED LOSS", value = kpi_el)
    with col2:
        st.write('It is recommended to apply a surcharge of (Euros):')
        st.metric(label="RECOMMENDED FEE", value = kpi_el * 3) 

else:
    st.write('DEFINE THE LOAN PARAMETERS AND CLICK ON CALCULATE RISK')









































