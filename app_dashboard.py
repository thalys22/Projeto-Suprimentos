import streamlit as st
import pandas as pd
import plotly.express as px
from db import engine

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Inflação de Insumos",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Gestão de Suprimentos - Análise de Inflação")
st.markdown("---")

# Funções de carregamento de dados
@st.cache_data
def load_data(query):
    return pd.read_sql(query, engine)

# Sidebar - Filtros
st.sidebar.header("Filtros")
try:
    regionais_df = load_data("SELECT DISTINCT regional FROM view_inflacao_mensal")
    regionais = regionais_df['regional'].tolist() if not regionais_df.empty else []
    regional_selecionada = st.sidebar.multiselect("Selecione as Regionais", regionais, default=regionais)
except Exception as e:
    st.sidebar.warning(f"Erro ao carregar regionais: {e}")
    regional_selecionada = []

# --- 1. VISÃO GLOBAL ---
st.header("📈 Evolução da Inflação")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Inflação Global Ponderada")
    try:
        df_global = load_data("SELECT * FROM view_inflacao_global ORDER BY mes")
        if not df_global.empty:
            fig_global = px.line(df_global, x='mes', y='inflacao_global_ponderada', 
                                 title="Índice de Inflação Global (%)",
                                 labels={'inflacao_global_ponderada': 'Inflação (%)', 'mes': 'Mês'},
                                 markers=True)
            st.plotly_chart(fig_global, use_container_width=True)
        else:
            st.info("Sem dados globais para exibir.")
    except Exception as e:
        st.error(f"Erro ao carregar inflação global: {e}")

with col2:
    st.subheader("Inflação por Regional")
    try:
        if regional_selecionada:
            # Construção segura da query para evitar erros de sintaxe
            placeholder = ', '.join([f"'{r}'" for r in regional_selecionada])
            query_reg = f"SELECT * FROM view_inflacao_mensal WHERE regional IN ({placeholder}) ORDER BY mes"
            df_reg = load_data(query_reg)
            if not df_reg.empty:
                fig_reg = px.line(df_reg, x='mes', y='inflacao_mensal_regional', color='regional',
                                  title="Inflação por Regional (%)",
                                  labels={'inflacao_mensal_regional': 'Inflação (%)', 'mes': 'Mês'},
                                  markers=True)
                st.plotly_chart(fig_reg, use_container_width=True)
            else:
                st.info("Sem dados para as regionais selecionadas.")
        else:
            st.info("Selecione ao menos uma regional.")
    except Exception as e:
        st.error(f"Erro ao carregar inflação regional: {e}")

st.markdown("---")

# --- 2. ANÁLISE POR CLASSE ABC ---
st.header("📊 Inflação por Classe ABC")
try:
    if regional_selecionada:
        placeholder = ', '.join([f"'{r}'" for r in regional_selecionada])
        query_abc = f"SELECT * FROM view_inflacao_por_classe_abc WHERE regional IN ({placeholder}) ORDER BY mes, classe_abc"
        df_abc_inflacao = load_data(query_abc)
        if not df_abc_inflacao.empty:
            fig_abc_bar = px.bar(df_abc_inflacao, x='mes', y='inflacao_classe', color='classe_abc',
                                 barmode='group', title="Inflação Mensal por Classe ABC (%)",
                                 labels={'inflacao_classe': 'Inflação (%)', 'mes': 'Mês', 'classe_abc': 'Classe'})
            st.plotly_chart(fig_abc_bar, use_container_width=True)
        else:
            st.info("Sem dados de inflação por classe ABC.")
except Exception as e:
    st.error(f"Erro ao carregar inflação por classe ABC: {e}")

st.markdown("---")

# --- 3. DETALHAMENTO DE IMPACTO ---
st.header("🔍 Detalhamento de Impacto")
tab1, tab2, tab3 = st.tabs(["Por Insumo (Vilões)", "Por Grupo", "Distribuição Cesta"])

with tab1:
    st.subheader("Maiores Impactos na Inflação (Top 10)")
    try:
        df_insumos = load_data("SELECT * FROM view_inflacao_por_insumo LIMIT 10")
        if not df_insumos.empty:
            st.dataframe(df_insumos.style.format({'variacao_percentual': '{:.2f}%', 'impacto_inflacao': '{:.2f}%'}), use_container_width=True)
        else:
            st.info("Sem dados de insumos.")
    except Exception as e:
        st.error(f"Erro ao carregar detalhes por insumo: {e}")

with tab2:
    st.subheader("Inflação por Grupo de Insumo")
    try:
        df_grupo = load_data("SELECT * FROM view_inflacao_por_grupo")
        if not df_grupo.empty:
            fig_grupo = px.bar(df_grupo, x='mes', y='inflacao_grupo', color='grupo_de_insumo', barmode='group',
                               title="Impacto por Grupo de Insumo (%)",
                               labels={'inflacao_grupo': 'Impacto (%)', 'mes': 'Mês'})
            st.plotly_chart(fig_grupo, use_container_width=True)
        else:
            st.info("Sem dados por grupo.")
    except Exception as e:
        st.error(f"Erro ao carregar detalhes por grupo: {e}")

with tab3:
    st.subheader("Distribuição da Curva ABC (Pesos)")
    try:
        df_abc_dist = load_data("SELECT classe_abc, SUM(valor_total_insumo) as valor FROM view_curva_abc_insumos GROUP BY classe_abc")
        if not df_abc_dist.empty:
            fig_abc_pie = px.pie(df_abc_dist, values='valor', names='classe_abc', title="Participação Financeira na Cesta")
            st.plotly_chart(fig_abc_pie, use_container_width=True)
        else:
            st.info("Sem dados da curva ABC.")
    except Exception as e:
        st.error(f"Erro ao carregar curva ABC: {e}")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("Desenvolvido para Gestão de Suprimentos")
