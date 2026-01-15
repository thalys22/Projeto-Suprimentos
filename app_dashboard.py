import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from db import engine
from sqlalchemy import text
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Inflação de Insumos",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Gestão de Suprimentos - Análise de Inflação")
st.markdown("---")

# Funções de carregamento de dados seguras
@st.cache_data(ttl=3600)
def load_data_safe(query, params=None):
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- SIDEBAR: FILTROS GLOBAIS ---
st.sidebar.header("⚙️ Filtros Globais")

# Carregar datas disponíveis
df_datas = load_data_safe("SELECT DISTINCT mes FROM view_inflacao_mensal ORDER BY mes DESC")
if not df_datas.empty:
    datas_disponiveis = pd.to_datetime(df_datas['mes']).dt.date.tolist()
    data_inicio = st.sidebar.date_input("Data Inicial", value=datas_disponiveis[-1] if datas_disponiveis else datetime.now())
    data_fim = st.sidebar.date_input("Data Final", value=datas_disponiveis[0] if datas_disponiveis else datetime.now())
else:
    data_inicio = st.sidebar.date_input("Data Inicial")
    data_fim = st.sidebar.date_input("Data Final")

# Carregar regionais
df_regionais = load_data_safe("SELECT DISTINCT regional FROM view_inflacao_mensal")
regionais = df_regionais['regional'].tolist() if not df_regionais.empty else []
regional_selecionada = st.sidebar.multiselect("Selecione as Regionais", regionais, default=regionais)

# --- CARDS DE TENDÊNCIA NO TOPO ---
st.header("📊 Indicadores Principais")
col1, col2, col3 = st.columns(3)

with col1:
    df_global = load_data_safe("""
        SELECT mes, inflacao_global_ponderada, inflacao_global_acumulada_ano 
        FROM view_inflacao_global 
        WHERE mes >= :inicio AND mes <= :fim
        ORDER BY mes DESC LIMIT 2
    """, {"inicio": data_inicio, "fim": data_fim})
    
    if not df_global.empty:
        atual = df_global.iloc[0]['inflacao_global_ponderada']
        anterior = df_global.iloc[1]['inflacao_global_ponderada'] if len(df_global) > 1 else atual
        tendencia = atual - anterior
        ano_ref = pd.to_datetime(df_global.iloc[0]['mes']).year
        
        st.metric(
            label=f"Inflação Mensal Global ({ano_ref})",
            value=f"{atual:.2f}%",
            delta=f"{tendencia:.2f}%",
            delta_color="inverse"
        )
    else:
        st.info("Sem dados globais")

with col2:
    if not df_global.empty:
        acumulada = df_global.iloc[0]['inflacao_global_acumulada_ano']
        st.metric(label="Inflação Acumulada (Ano)", value=f"{acumulada:.2f}%")
    else:
        st.info("Sem dados acumulados")

with col3:
    df_meta = load_data_safe("""
        SELECT evolucao_mensal * 100 as meta_mensal 
        FROM metas_incc 
        WHERE mes_referencia >= :inicio AND mes_referencia <= :fim
        ORDER BY mes_referencia DESC LIMIT 1
    """, {"inicio": data_inicio, "fim": data_fim})
    
    if not df_meta.empty:
        meta = df_meta.iloc[0]['meta_mensal']
        st.metric(label="Meta Mensal (50% INCC-M)", value=f"{meta:.2f}%")
    else:
        st.info("Sem meta definida")

st.markdown("---")

# --- GRÁFICO: EVOLUÇÃO DA INFLAÇÃO COM METAS E RÓTULOS ---
st.header("📈 Evolução da Inflação vs Meta")

if regional_selecionada:
    df_evolucao = load_data_safe("""
        SELECT mes, inflacao_mensal_regional, regional
        FROM view_inflacao_mensal
        WHERE regional IN :regionais AND mes >= :inicio AND mes <= :fim
        ORDER BY mes
    """, {"regionais": tuple(regional_selecionada), "inicio": data_inicio, "fim": data_fim})
    
    df_metas = load_data_safe("""
        SELECT mes_referencia, evolucao_mensal * 100 as meta_mensal
        FROM metas_incc
        WHERE mes_referencia >= :inicio AND mes_referencia <= :fim
        ORDER BY mes_referencia
    """, {"inicio": data_inicio, "fim": data_fim})
    
    if not df_evolucao.empty:
        fig = go.Figure()
        for reg in regional_selecionada:
            dfr = df_evolucao[df_evolucao['regional'] == reg]
            fig.add_trace(go.Scatter(
                x=dfr['mes'], y=dfr['inflacao_mensal_regional'],
                mode='lines+markers+text', name=f'Inflação {reg}',
                text=[f"{v:.1f}%" for v in dfr['inflacao_mensal_regional']],
                textposition="top center"
            ))
        
        if not df_metas.empty:
            fig.add_trace(go.Scatter(
                x=df_metas['mes_referencia'], y=df_metas['meta_mensal'],
                mode='lines', name='Meta (50% INCC-M)',
                line=dict(color='yellow', width=3, dash='dash')
            ))
        
        fig.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- GRÁFICO: INFLAÇÃO POR CLASSE ABC (LINHAS COM RÓTULOS) ---
st.header("🔤 Inflação por Classe ABC")
classes_disp = ['A', 'B', 'C']
classes_sel = st.multiselect("Filtrar Classe", classes_disp, default=classes_disp)

if regional_selecionada and classes_sel:
    df_abc = load_data_safe("""
        SELECT mes, classe_abc, SUM(inflacao_classe) as inflacao_classe
        FROM view_inflacao_por_classe_abc
        WHERE regional IN :regionais AND classe_abc IN :classes
        AND mes >= :inicio AND mes <= :fim
        GROUP BY 1, 2 ORDER BY 1
    """, {"regionais": tuple(regional_selecionada), "classes": tuple(classes_sel), "inicio": data_inicio, "fim": data_fim})
    
    if not df_abc.empty:
        fig_abc = px.line(df_abc, x='mes', y='inflacao_classe', color='classe_abc', markers=True, text=df_abc['inflacao_classe'].apply(lambda x: f"{x:.1f}%"))
        fig_abc.update_traces(textposition="top center")
        st.plotly_chart(fig_abc, use_container_width=True)

st.markdown("---")

# --- GRÁFICO: INFLAÇÃO POR GRUPO (LINHAS COM RÓTULOS) ---
st.header("📦 Inflação por Grupo de Insumo")
df_grupos = load_data_safe("SELECT DISTINCT grupo_de_insumo FROM view_inflacao_por_grupo")
grupos_sel = st.multiselect("Filtrar Grupos", df_grupos['grupo_de_insumo'].tolist(), default=df_grupos['grupo_de_insumo'].tolist()[:5])

if regional_selecionada and grupos_sel:
    df_g = load_data_safe("""
        SELECT mes, grupo_de_insumo, SUM(inflacao_grupo) as inflacao_grupo
        FROM view_inflacao_por_grupo
        WHERE regional IN :regionais AND grupo_de_insumo IN :grupos
        AND mes >= :inicio AND mes <= :fim
        GROUP BY 1, 2 ORDER BY 1
    """, {"regionais": tuple(regional_selecionada), "grupos": tuple(grupos_sel), "inicio": data_inicio, "fim": data_fim})
    
    if not df_g.empty:
        fig_g = px.line(df_g, x='mes', y='inflacao_grupo', color='grupo_de_insumo', markers=True, text=df_g['inflacao_grupo'].apply(lambda x: f"{x:.1f}%"))
        fig_g.update_traces(textposition="top center")
        st.plotly_chart(fig_g, use_container_width=True)

st.markdown("---")

# --- TABELA: VILÕES (CORREÇÃO DE ASPAS) ---
st.header("🚨 Vilões - Insumos com Maior Impacto")
df_ins_disp = load_data_safe("SELECT DISTINCT descricao_insumo FROM view_inflacao_por_insumo ORDER BY 1")
ins_sel = st.multiselect("Filtrar Insumos", df_ins_disp['descricao_insumo'].tolist(), default=df_ins_disp['descricao_insumo'].tolist()[:10])

if ins_sel:
    df_v = load_data_safe("""
        SELECT mes, descricao_insumo, impacto_inflacao
        FROM view_inflacao_por_insumo
        WHERE descricao_insumo IN :insumos AND mes >= :inicio AND mes <= :fim
        ORDER BY mes DESC, impacto_inflacao DESC
    """, {"insumos": tuple(ins_sel), "inicio": data_inicio, "fim": data_fim})
    
    if not df_v.empty:
        df_v['Impacto (%)'] = df_v['impacto_inflacao'].apply(lambda x: f"{x:.2f}%")
        st.dataframe(df_v[['mes', 'descricao_insumo', 'Impacto (%)']], use_container_width=True)

st.markdown("---")

# --- ANÁLISE POR FORNECEDOR (LINHAS E FILTRO) ---
st.header("🏢 Variação de Preços por Fornecedor")
df_forn_disp = load_data_safe("SELECT DISTINCT fornecedor FROM view_inflacao_por_fornecedor ORDER BY 1")
forn_sel = st.multiselect("Filtrar Fornecedores", df_forn_disp['fornecedor'].tolist(), default=df_forn_disp['fornecedor'].tolist()[:5])

if forn_sel:
    df_f = load_data_safe("""
        SELECT mes, fornecedor, variacao_media_precos
        FROM view_inflacao_por_fornecedor
        WHERE fornecedor IN :fornecedores AND mes >= :inicio AND mes <= :fim
        ORDER BY mes
    """, {"fornecedores": tuple(forn_sel), "inicio": data_inicio, "fim": data_fim})
    
    if not df_f.empty:
        # Tratar NaN e formatar
        df_f['variacao_media_precos'] = df_f['variacao_media_precos'].fillna(0)
        fig_f = px.line(df_f, x='mes', y='variacao_media_precos', color='fornecedor', markers=True, text=df_f['variacao_media_precos'].apply(lambda x: f"{x:.1f}%"))
        fig_f.update_traces(textposition="top center")
        st.plotly_chart(fig_f, use_container_width=True)
        
        df_f['Variação (%)'] = df_f['variacao_media_precos'].apply(lambda x: f"{x:.2f}%")
        st.dataframe(df_f[['mes', 'fornecedor', 'Variação (%)']], use_container_width=True)
