import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from db import engine
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Inflação de Insumos",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Gestão de Suprimentos - Análise de Inflação")
st.markdown("---")

# Funções de carregamento de dados
@st.cache_data(ttl=3600)
def load_data(query):
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- SIDEBAR: FILTROS GLOBAIS ---
st.sidebar.header("⚙️ Filtros Globais")

# Carregar datas disponíveis
df_datas = load_data("SELECT DISTINCT mes FROM view_inflacao_mensal ORDER BY mes DESC")
if not df_datas.empty:
    datas_disponiveis = pd.to_datetime(df_datas['mes']).dt.date.tolist()
    data_inicio = st.sidebar.date_input("Data Inicial", value=datas_disponiveis[-1] if datas_disponiveis else datetime.now())
    data_fim = st.sidebar.date_input("Data Final", value=datas_disponiveis[0] if datas_disponiveis else datetime.now())
else:
    data_inicio = st.sidebar.date_input("Data Inicial")
    data_fim = st.sidebar.date_input("Data Final")

# Carregar regionais
df_regionais = load_data("SELECT DISTINCT regional FROM view_inflacao_mensal")
regionais = df_regionais['regional'].tolist() if not df_regionais.empty else []
regional_selecionada = st.sidebar.multiselect("Selecione as Regionais", regionais, default=regionais)

# --- CARDS DE TENDÊNCIA NO TOPO ---
st.header("📊 Indicadores Principais")
col1, col2, col3 = st.columns(3)

with col1:
    try:
        df_global_latest = load_data(f"""
            SELECT inflacao_global_ponderada, inflacao_global_acumulada_ano 
            FROM view_inflacao_global 
            WHERE mes >= '{data_inicio}' AND mes <= '{data_fim}'
            ORDER BY mes DESC LIMIT 2
        """)
        if not df_global_latest.empty:
            inflacao_atual = df_global_latest.iloc[0]['inflacao_global_ponderada']
            inflacao_anterior = df_global_latest.iloc[1]['inflacao_global_ponderada'] if len(df_global_latest) > 1 else inflacao_atual
            tendencia = inflacao_atual - inflacao_anterior
            
            cor = "🔴" if tendencia > 0 else "🟢"
            st.metric(
                label="Inflação Mensal Global",
                value=f"{inflacao_atual:.2f}%",
                delta=f"{tendencia:.2f}%",
                delta_color="inverse"
            )
        else:
            st.info("Sem dados disponíveis")
    except Exception as e:
        st.error(f"Erro ao carregar indicador: {e}")

with col2:
    try:
        df_acumulada = load_data(f"""
            SELECT inflacao_global_acumulada_ano 
            FROM view_inflacao_global 
            WHERE mes >= '{data_inicio}' AND mes <= '{data_fim}'
            ORDER BY mes DESC LIMIT 1
        """)
        if not df_acumulada.empty:
            acumulada = df_acumulada.iloc[0]['inflacao_global_acumulada_ano']
            st.metric(label="Inflação Acumulada (Ano)", value=f"{acumulada:.2f}%")
        else:
            st.info("Sem dados disponíveis")
    except Exception as e:
        st.error(f"Erro ao carregar acumulada: {e}")

with col3:
    try:
        df_meta = load_data(f"""
            SELECT (evolucao_mensal * 50) as meta_mensal 
            FROM metas_incc 
            WHERE mes_referencia >= '{data_inicio}' AND mes_referencia <= '{data_fim}'
            ORDER BY mes_referencia DESC LIMIT 1
        """)
        if not df_meta.empty:
            meta = df_meta.iloc[0]['meta_mensal'] * 100
            st.metric(label="Meta Mensal (50% INCC-M)", value=f"{meta:.2f}%")
        else:
            st.info("Sem meta disponível")
    except Exception as e:
        st.error(f"Erro ao carregar meta: {e}")

st.markdown("---")

# --- GRÁFICO: EVOLUÇÃO DA INFLAÇÃO COM METAS ---
st.header("📈 Evolução da Inflação")

try:
    if regional_selecionada:
        placeholder = ', '.join([f"'{r}'" for r in regional_selecionada])
        query_evolucao = f"""
            SELECT mes, inflacao_mensal_regional, inflacao_acumulada_ano, regional
            FROM view_inflacao_mensal
            WHERE regional IN ({placeholder}) AND mes >= '{data_inicio}' AND mes <= '{data_fim}'
            ORDER BY mes
        """
        df_evolucao = load_data(query_evolucao)
        
        # Carregar metas
        df_metas = load_data(f"""
            SELECT mes_referencia, (evolucao_mensal * 50) * 100 as meta_mensal, 
                   (acumulado_12_meses * 50) * 100 as meta_acumulada
            FROM metas_incc
            WHERE mes_referencia >= '{data_inicio}' AND mes_referencia <= '{data_fim}'
            ORDER BY mes_referencia
        """)
        
        if not df_evolucao.empty:
            fig = go.Figure()
            
            # Adicionar linhas de inflação por regional
            for regional in regional_selecionada:
                df_regional = df_evolucao[df_evolucao['regional'] == regional]
                fig.add_trace(go.Scatter(
                    x=df_regional['mes'], y=df_regional['inflacao_mensal_regional'],
                    mode='lines+markers', name=f'Inflação {regional}',
                    line=dict(width=2)
                ))
            
            # Adicionar linha de meta (amarela)
            if not df_metas.empty:
                fig.add_trace(go.Scatter(
                    x=df_metas['mes_referencia'], y=df_metas['meta_mensal'],
                    mode='lines', name='Meta Mensal (50% INCC-M)',
                    line=dict(color='yellow', width=3, dash='dash')
                ))
            
            fig.update_layout(
                title="Inflação Mensal vs Meta",
                xaxis_title="Mês",
                yaxis_title="Inflação (%)",
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados para o período selecionado")
    else:
        st.warning("Selecione ao menos uma regional")
except Exception as e:
    st.error(f"Erro ao carregar gráfico de evolução: {e}")

st.markdown("---")

# --- GRÁFICO: INFLAÇÃO ACUMULADA ---
st.header("📊 Inflação Acumulada no Ano")

try:
    if regional_selecionada:
        placeholder = ', '.join([f"'{r}'" for r in regional_selecionada])
        query_acumulada = f"""
            SELECT mes, inflacao_acumulada_ano, regional
            FROM view_inflacao_mensal
            WHERE regional IN ({placeholder}) AND mes >= '{data_inicio}' AND mes <= '{data_fim}'
            ORDER BY mes
        """
        df_acumulada = load_data(query_acumulada)
        
        if not df_acumulada.empty:
            fig_acum = px.line(df_acumulada, x='mes', y='inflacao_acumulada_ano', color='regional',
                               title="Inflação Acumulada (Ano Civil)",
                               labels={'inflacao_acumulada_ano': 'Inflação Acumulada (%)', 'mes': 'Mês'},
                               markers=True)
            st.plotly_chart(fig_acum, use_container_width=True)
        else:
            st.info("Sem dados para o período selecionado")
    else:
        st.warning("Selecione ao menos uma regional")
except Exception as e:
    st.error(f"Erro ao carregar gráfico acumulado: {e}")

st.markdown("---")

# --- ANÁLISE POR CLASSE ABC ---
st.header("🔤 Inflação por Classe ABC")

try:
    if regional_selecionada:
        placeholder = ', '.join([f"'{r}'" for r in regional_selecionada])
        
        # Filtro de classe ABC
        classes_disponiveis = ['A', 'B', 'C']
        classes_selecionadas = st.multiselect("Filtrar por Classe ABC", classes_disponiveis, default=classes_disponiveis)
        
        if classes_selecionadas:
            classes_placeholder = ', '.join([f"'{c}'" for c in classes_selecionadas])
            query_abc = f"""
                SELECT mes, regional, classe_abc, inflacao_classe
                FROM view_inflacao_por_classe_abc
                WHERE regional IN ({placeholder}) AND classe_abc IN ({classes_placeholder})
                AND mes >= '{data_inicio}' AND mes <= '{data_fim}'
                ORDER BY mes
            """
            df_abc = load_data(query_abc)
            
            if not df_abc.empty:
                fig_abc = px.line(df_abc, x='mes', y='inflacao_classe', color='classe_abc',
                                  title="Inflação por Classe ABC (%)",
                                  labels={'inflacao_classe': 'Inflação (%)', 'mes': 'Mês'},
                                  markers=True)
                st.plotly_chart(fig_abc, use_container_width=True)
            else:
                st.info("Sem dados para o período selecionado")
except Exception as e:
    st.error(f"Erro ao carregar inflação por classe ABC: {e}")

st.markdown("---")

# --- ANÁLISE POR GRUPO DE INSUMO ---
st.header("📦 Inflação por Grupo de Insumo")

try:
    if regional_selecionada:
        placeholder = ', '.join([f"'{r}'" for r in regional_selecionada])
        
        # Carregar grupos disponíveis
        df_grupos_disp = load_data(f"""
            SELECT DISTINCT grupo_de_insumo FROM view_inflacao_por_grupo
            WHERE regional IN ({placeholder})
        """)
        grupos_disponiveis = df_grupos_disp['grupo_de_insumo'].tolist() if not df_grupos_disp.empty else []
        grupos_selecionados = st.multiselect("Filtrar por Grupo de Insumo", grupos_disponiveis, default=grupos_disponiveis[:5] if grupos_disponiveis else [])
        
        if grupos_selecionados:
            grupos_placeholder = ', '.join([f"'{g}'" for g in grupos_selecionados])
            query_grupo = f"""
                SELECT mes, regional, grupo_de_insumo, inflacao_grupo
                FROM view_inflacao_por_grupo
                WHERE regional IN ({placeholder}) AND grupo_de_insumo IN ({grupos_placeholder})
                AND mes >= '{data_inicio}' AND mes <= '{data_fim}'
                ORDER BY mes
            """
            df_grupo = load_data(query_grupo)
            
            if not df_grupo.empty:
                fig_grupo = px.line(df_grupo, x='mes', y='inflacao_grupo', color='grupo_de_insumo',
                                    title="Inflação por Grupo de Insumo (%)",
                                    labels={'inflacao_grupo': 'Inflação (%)', 'mes': 'Mês'},
                                    markers=True)
                st.plotly_chart(fig_grupo, use_container_width=True)
            else:
                st.info("Sem dados para o período selecionado")
except Exception as e:
    st.error(f"Erro ao carregar inflação por grupo: {e}")

st.markdown("---")

# --- TABELA: VILÕES (INSUMOS COM MAIOR IMPACTO) ---
st.header("🚨 Vilões - Insumos com Maior Impacto")

try:
    # Filtro de insumo
    df_insumos_disp = load_data("SELECT DISTINCT descricao_insumo FROM view_inflacao_por_insumo")
    insumos_disponiveis = df_insumos_disp['descricao_insumo'].tolist() if not df_insumos_disp.empty else []
    insumos_selecionados = st.multiselect("Filtrar por Insumo", insumos_disponiveis, default=insumos_disponiveis[:10] if insumos_disponiveis else [])
    
    if insumos_selecionados:
        insumos_placeholder = ', '.join([f"'{i}'" for i in insumos_selecionados])
        query_viloes = f"""
            SELECT mes, descricao_insumo, impacto_inflacao
            FROM view_inflacao_por_insumo
            WHERE descricao_insumo IN ({insumos_placeholder})
            AND mes >= '{data_inicio}' AND mes <= '{data_fim}'
            ORDER BY mes DESC, impacto_inflacao DESC
        """
        df_viloes = load_data(query_viloes)
        
        if not df_viloes.empty:
            df_viloes['mes'] = pd.to_datetime(df_viloes['mes']).dt.strftime('%Y-%m-%d')
            df_viloes['Impacto (%)'] = df_viloes['impacto_inflacao'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(df_viloes[['mes', 'descricao_insumo', 'Impacto (%)']].rename(
                columns={'mes': 'Data', 'descricao_insumo': 'Insumo'}
            ), use_container_width=True)
        else:
            st.info("Sem dados para o período selecionado")
except Exception as e:
    st.error(f"Erro ao carregar vilões: {e}")

st.markdown("---")

# --- ANÁLISE POR FORNECEDOR ---
st.header("🏢 Variação de Preços por Fornecedor")

try:
    query_fornecedor = f"""
        SELECT mes, fornecedor, variacao_media_precos
        FROM view_inflacao_por_fornecedor
        WHERE mes >= '{data_inicio}' AND mes <= '{data_fim}'
        ORDER BY mes DESC
    """
    df_fornecedor = load_data(query_fornecedor)
    
    if not df_fornecedor.empty:
        fig_forn = px.bar(df_fornecedor, x='mes', y='variacao_media_precos', color='fornecedor',
                          title="Variação Média de Preços por Fornecedor (%)",
                          labels={'variacao_media_precos': 'Variação (%)', 'mes': 'Mês'},
                          barmode='group')
        st.plotly_chart(fig_forn, use_container_width=True)
        
        st.subheader("Tabela Detalhada por Fornecedor")
        df_forn_tabela = df_fornecedor.copy()
        df_forn_tabela['mes'] = pd.to_datetime(df_forn_tabela['mes']).dt.strftime('%Y-%m-%d')
        df_forn_tabela['Variação (%)'] = df_forn_tabela['variacao_media_precos'].apply(lambda x: f"{x:.2f}%")
        st.dataframe(df_forn_tabela[['mes', 'fornecedor', 'Variação (%)']].rename(
            columns={'mes': 'Data', 'fornecedor': 'Fornecedor'}
        ), use_container_width=True)
    else:
        st.info("Sem dados para o período selecionado")
except Exception as e:
    st.error(f"Erro ao carregar análise por fornecedor: {e}")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("Dashboard de Análise de Inflação de Insumos - Gestão de Suprimentos")
