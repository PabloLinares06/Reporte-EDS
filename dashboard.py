import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Business Intelligence | EDS Las Palmeras",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PROFESIONALES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #f0f2f6;
    }
    
    /* Estilo de Tarjetas Adaptable */
    div.stMetric {
        background-color: var(--secondary-background-color);
        border-radius: 12px;
        padding: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Títulos de Métricas */
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
    }
    
    /* Valores de Métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* Contenedores de Gráficos Adaptables */
    .plot-container {
        background-color: var(--secondary-background-color);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }

    /* Sidebar */
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf, #052b5e);
        color: white;
    }
    
    hr {
        margin: 1rem 0 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        color: var(--text-color);
    }

    .stTabs [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: white !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DE DATOS ---
@st.cache_data
def load_and_process_data():
    file_path = 'ANALISIS OPERATIVO LAS PALMERAS.xlsx'
    
    # Detalle Diario
    df_v = pd.read_excel(file_path, sheet_name='VENTAS X MES', header=2)
    df_v = df_v.iloc[:, [0, 1, 2, 4, 5, 7, 8]] 
    df_v.columns = ['Fecha', 'Corriente_Gal', 'Corriente_Pesos', 'ACPM_Gal', 'ACPM_Pesos', 'Urea_Litros', 'Urea_Pesos']
    df_v['Fecha'] = pd.to_datetime(df_v['Fecha'], errors='coerce')
    df_v = df_v.dropna(subset=['Fecha'])
    
    # Comparativos YoY
    df_s = pd.read_excel(file_path, sheet_name='ESTADISTICAS', header=1)
    comparativas = {
        'Corriente': df_s.iloc[:, [0, 1, 2, 3]].copy(),
        'ACPM': df_s.iloc[:, [6, 7, 8, 9]].copy(),
        'Urea': df_s.iloc[:, [12, 13, 14, 15]].copy()
    }
    
    for p in comparativas:
        comparativas[p].columns = ['F_Ant', 'V_Ant', 'F_Act', 'V_Act']
        comparativas[p]['F_Act'] = pd.to_datetime(comparativas[p]['F_Act'], errors='coerce')
        comparativas[p]['Dia'] = comparativas[p]['F_Act'].dt.day
        comparativas[p] = comparativas[p].dropna(subset=['F_Act'])
        comparativas[p]['V_Ant'] = pd.to_numeric(comparativas[p]['V_Ant'], errors='coerce').fillna(0)
        comparativas[p]['V_Act'] = pd.to_numeric(comparativas[p]['V_Act'], errors='coerce').fillna(0)
    
    return df_v, comparativas

# --- UI LOGIC ---
try:
    df_v, comparativas = load_and_process_data()

    # Sidebar Branding
    with st.sidebar:
        st.markdown("### 🏷️ Configuración")
        prods = ['Corriente', 'ACPM', 'Urea']
        sel_prods = st.multiselect("Visualizar productos:", prods, default=prods)
        st.markdown("---")
        st.markdown("### 📅 Periodo de Informe")
        st.info(f"**Mes:** {df_v['Fecha'].iloc[0].strftime('%B %Y')}")
        st.markdown("---")
        st.caption("v2.0 Professional Edition")

    # Header Pro
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("⛽ EDS Las Palmeras | Control Operativo")
        st.markdown("*Análisis avanzado de ventas y rendimiento interanual*")
    with col_h2:
        # Reloj o fecha actual
        st.markdown(f"**Fecha de Reporte:** {datetime.now().strftime('%d/%m/%Y')}")

    st.markdown("---")

    # Tabs Principal
    tab_resumen, tab_analisis, tab_yoy = st.tabs(["⚡ Panel de Control", "🔍 Detalle Analítico", "📈 Crecimiento Interanual"])

    # --- TAB 1: PANEL DE CONTROL ---
    with tab_resumen:
        # KPIs dinámicos
        v_pesos = 0
        v_gal = 0
        if 'Corriente' in sel_prods:
            v_pesos += df_v['Corriente_Pesos'].sum()
            v_gal += df_v['Corriente_Gal'].sum()
        if 'ACPM' in sel_prods:
            v_pesos += df_v['ACPM_Pesos'].sum()
            v_gal += df_v['ACPM_Gal'].sum()
        if 'Urea' in sel_prods:
            v_pesos += df_v['Urea_Pesos'].sum()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Ventas Totales", f"${v_pesos/1e6:,.1f}M", help="Total recaudado en millones de pesos")
        k2.metric("Volumen Combustible", f"{v_gal:,.0f} Gal", help="Suma de Corriente y ACPM")
        k3.metric("Eficiencia (Pesos/Gal)", f"${(v_pesos/v_gal if v_gal > 0 else 0):,.0f}")
        
        # Cálculo de crecimiento rápido para Corriente
        c_act = comparativas['Corriente']['V_Act'].sum()
        c_ant = comparativas['Corriente']['V_Ant'].sum()
        c_pct = ((c_act - c_ant)/c_ant * 100) if c_ant > 0 else 0
        k4.metric("Crecimiento Corriente", f"{c_pct:,.1f}%", delta=f"{c_pct:,.1f}%", delta_color="normal")

        st.markdown("#### 📊 Evolución del Volumen de Ventas")
        
        fig_evol = go.Figure()
        colors = {'Corriente': '#2563eb', 'ACPM': '#f59e0b', 'Urea': '#10b981'}
        
        if 'Corriente' in sel_prods:
            fig_evol.add_trace(go.Scatter(x=df_v['Fecha'], y=df_v['Corriente_Gal'], name='Corriente', 
                                         line=dict(color=colors['Corriente'], width=4), fill='tozeroy'))
        if 'ACPM' in sel_prods:
            fig_evol.add_trace(go.Scatter(x=df_v['Fecha'], y=df_v['ACPM_Gal'], name='ACPM', 
                                         line=dict(color=colors['ACPM'], width=4), fill='tonexty'))
            
        fig_evol.update_layout(
            template='plotly_white',
            hovermode="x unified",
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_evol, use_container_width=True)

    # --- TAB 2: DETALLE ANALÍTICO ---
    with tab_analisis:
        st.markdown("#### Segmentación por Línea de Negocio")
        
        c_pie, c_table = st.columns([1, 2])
        
        with c_pie:
            values = [df_v['Corriente_Pesos'].sum(), df_v['ACPM_Pesos'].sum(), df_v['Urea_Pesos'].sum()]
            fig_share = px.pie(names=['Corriente', 'ACPM', 'Urea'], values=values, hole=.5,
                               color_discrete_sequence=['#2563eb', '#f59e0b', '#10b981'])
            fig_share.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_share, use_container_width=True)
            
        with c_table:
            st.markdown("###### Registro de Ventas (Abril 2026)")
            st.dataframe(df_v.set_index('Fecha'), use_container_width=True, height=350)

        st.markdown("---")
        st.markdown("#### 🌡️ Correlación Precio-Volumen")
        p_sel = st.selectbox("Seleccione producto para analizar correlación:", sel_prods)
        col_g = f"{p_sel}_{'Gal' if p_sel != 'Urea' else 'Litros'}"
        col_p = f"{p_sel}_Pesos"
        
        fig_corr = px.scatter(df_v, x=col_g, y=col_p, trendline="ols", trendline_color_override="red",
                              labels={col_g: "Volumen Vendido", col_p: "Ingresos (COP)"},
                              template="plotly_white")
        st.plotly_chart(fig_corr, use_container_width=True)

    # --- TAB 3: CRECIMIENTO YoY ---
    with tab_yoy:
        st.markdown("#### 🔄 Comparativa de Rendimiento: 2025 vs 2026")
        p_comp = st.radio("Producto a comparar:", prods, horizontal=True)
        
        df_c = comparativas[p_comp]
        
        fig_yoy = go.Figure()
        fig_yoy.add_trace(go.Bar(x=df_c['Dia'], y=df_c['V_Ant'], name='2025 (Año Anterior)', marker_color='#cbd5e1'))
        fig_yoy.add_trace(go.Bar(x=df_c['Dia'], y=df_c['V_Act'], name='2026 (Actual)', marker_color='#2563eb'))
        
        fig_yoy.update_layout(
            template='plotly_white',
            barmode='group',
            height=500,
            xaxis=dict(title="Día del Mes", tickmode='linear'),
            yaxis=dict(title="Volumen (Gal/Lt)"),
            margin=dict(t=50)
        )
        st.plotly_chart(fig_yoy, use_container_width=True)
        
        # Insights interanuales
        sum_act = df_c['V_Act'].sum()
        sum_ant = df_c['V_Ant'].sum()
        diff = sum_act - sum_ant
        
        st.success(f"**Resultado del Análisis:** Para {p_comp}, hay una diferencia de **{diff:+,.2f}** unidades respecto al año anterior.")

except Exception as e:
    st.error(f"❌ Error Crítico: {e}")
    st.warning("Verifica que el archivo Excel no esté abierto en otra aplicación y que las hojas 'VENTAS X MES' y 'ESTADISTICAS' existan.")
