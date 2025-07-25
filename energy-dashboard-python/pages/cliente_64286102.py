# pages/6_Cliente_64286102.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import io # Para lidar com a leitura de arquivos em memória

# --- Inicialização Robusta do Session State ---
# Garante que 'all_clients_data' exista, mesmo se a página for acessada diretamente.
if 'all_clients_data' not in st.session_state:
    st.session_state.all_clients_data = pd.DataFrame()

# --- CSS (Copiado do dashboard.py para consistência de estilo) ---
st.markdown("""
<style>
    /* Ajuste global do tamanho da fonte e espaçamento para um visual mais compacto */
    html, body, .stApp {
        font-size: 14px; /* Tamanho de fonte base menor */
    }

    /* Main container styling */
    .main {
        padding: 0.5rem 0.5rem; /* Reduzido */
        background: #f8fafc;
    }

    /* Header styling */
    .main-header {
        font-size: 2rem; /* Reduzido */
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0.25rem; /* Reduzido */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .sub-header {
        font-size: 1rem; /* Reduzido */
        color: #64748b;
        text-align: center;
        margin-bottom: 1.5rem; /* Reduzido */
        font-weight: 400;
    }

    /* Metric cards */
    .metric-container {
        background: white;
        border-radius: 10px; /* Levemente reduzido */
        padding: 1rem; /* Reduzido */
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08); /* Sombra mais suave */
        border: 1px solid #e2e8f0;
        margin-bottom: 0.75rem; /* Reduzido */
    }

    .metric-title {
        font-size: 0.8rem; /* Reduzido */
        font-weight: 600;
        color: #475569;
        margin-bottom: 0.25rem; /* Reduzido */
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-value {
        font-size: 1.75rem; /* Reduzido */
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.15rem; /* Reduzido */
    }

    .metric-change {
        font-size: 0.8rem; /* Reduzido */
        font-weight: 500;
    }

    .metric-positive {
        color: #059669;
    }

    .metric-negative {
        color: #dc2626;
    }

    /* Contêiner do gráfico */
    .chart-container {
        background: white;
        border-radius: 10px; /* Levemente reduzido */
        padding: 1.25rem; /* Reduzido */
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08); /* Sombra mais suave */
        border: 1px solid #e2e8f0;
        margin-bottom: 1.25rem; /* Reduzido */
        margin-top: 0 !important; /* Adicionado para remover espaço superior */
    }

    .chart-title {
        font-size: 1.15rem; /* Reduzido */
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.75rem; /* Reduzido */
    }

    /* Estilo para os títulos dos gráficos com destaque */
    .chart-title-highlight {
        background: #f0f8ff; /* Um azul bem claro */
        border-left: 4px solid #3b82f6; /* Uma barra azul à esquerda */
        padding: 0.6rem 0.8rem; /* Reduzido */
        margin-bottom: 0.8rem; /* Reduzido */
        border-radius: 6px; /* Levemente reduzido */
        font-size: 1.2rem; /* Reduzido */
        font-weight: 700;
        color: #1e3a8a; /* Azul escuro para o texto */
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06); /* Sombra mais suave */
    }


    /* Estilo da barra lateral */
    .sidebar .sidebar-content {
        background: white;
        border-right: 1px solid #e2e8f0;
    }

    /* Estilo do botão */
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px; /* Levemente reduzido */
        padding: 0.4rem 0.8rem; /* Reduzido */
        font-weight: 500;
        transition: all 0.2s;
        font-size: 0.9rem; /* Reduzido */
    }

    .stButton > button:hover {
        background: #2563eb;
        transform: translateY(-1px);
    }

    /* Estilo para os "botões" de outras unidades */
    .unit-button {
        display: block;
        background: #e0f2f7; /* Cor clara para o botão */
        color: #0288d1; /* Cor do texto */
        border: 1px solid #81d4fa; /* Borda levemente mais escura */
        border-radius: 6px; /* Levemente reduzido */
        padding: 0.6rem 0.8rem; /* Reduzido */
        margin-bottom: 0.6rem; /* Reduzido */
        text-align: center;
        font-weight: 600;
        text-decoration: none; /* Remover sublinhado */
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); /* Sombra mais suave */
        font-size: 0.95rem; /* Reduzido */
    }

    .unit-button:hover {
        background: #b3e5fc;
        color: #01579b;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); /* Sombra mais suave */
        transform: translateY(-1px); /* Menor movimento */
    }

    /* Ocultar a marca Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Ajuste para o texto de informações abaixo dos títulos dos gráficos */
    p {
        font-size: 0.9rem; /* Reduzido */
        margin-top: 0.5rem; /* Ajustado */
        margin-bottom: 0.5rem; /* Ajustado */
    }
</style>
""", unsafe_allow_html=True)

# --- Funções Reutilizáveis para Gráficos e Métricas ---
# Estas funções são cópias das funções genéricas do dashboard.py
# para que cada página de cliente seja autocontida.

def display_metrics(df_filtered, enel_rate):
    """Exibe os cartões de métricas para os dados filtrados."""
    total_solar_generation = df_filtered['solar_generation'].sum()
    total_enel_consumption = df_filtered['enel_consumption'].sum()
    total_enel_cost = df_filtered['enel_cost'].sum()
    total_solar_savings = df_filtered['solar_savings'].sum()
    total_net_cost = df_filtered['net_cost'].sum()

    coverage_percentage = (total_solar_generation / total_enel_consumption) * 100 if total_enel_consumption > 0 else 0
    savings_vs_enel_only_pct = (total_solar_savings / total_enel_cost) * 100 if total_enel_cost > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">Geração Solar Total</div>
            <div class="metric-value">{total_solar_generation:.1f} kWh</div>
            <div class="metric-change metric-positive">Cobre {coverage_percentage:.1f}% do consumo</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">Consumo ENEL Total</div>
            <div class="metric-value">{total_enel_consumption:.1f} kWh</div>
            <div class="metric-change">Custo Original: €{total_enel_cost:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">Economia Solar</div>
            <div class="metric-value">€{total_solar_savings:.2f}</div>
            <div class="metric-change metric-positive">Reduz o custo em {savings_vs_enel_only_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">Custo Líquido</div>
            <div class="metric-value">€{total_net_cost:.2f}</div>
            <div class="metric-change metric-positive">Você economizou €{total_enel_cost - total_net_cost:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

def display_daily_charts(df_filtered):
    """Exibe gráficos diários de energia e custo."""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Comparação Diária de Energia (Consumo vs. Geração)</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_filtered['date'], y=df_filtered['solar_generation'], name='Geração Solar', marker_color='#22c55e',
        hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Solar: %{y:.1f} kWh<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=df_filtered['date'], y=df_filtered['enel_consumption'], name='Consumo ENEL', marker_color='#ef4444',
        hovertemplate='<b>%{x|%d-%m-%Y}</b><br>ENEL: %{y:.1f} kWh<extra></extra>'
    ))
    fig.update_layout(height=400, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      xaxis_title="Data", yaxis_title="Energia (kWh)", hovermode='x unified', plot_bgcolor='white',
                      paper_bgcolor='white', font=dict(family="Segoe UI", size=12), margin=dict(l=0, r=0, t=40, b=0),
                      transition_duration=1000) # Animação
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Análise Diária de Custos</div>', unsafe_allow_html=True)
        fig_cost = go.Figure()
        fig_cost.add_trace(go.Scatter(
            x=df_filtered['date'], y=df_filtered['enel_cost'], mode='lines+markers', name='Custo ENEL Original',
            line=dict(color='#ef4444', width=2), marker=dict(size=6),
            hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Custo Original: €%{y:.2f}<extra></extra>'
        ))
        fig_cost.add_trace(go.Scatter(
            x=df_filtered['date'], y=df_filtered['net_cost'], mode='lines+markers', name='Custo Líquido (com Solar)',
            line=dict(color='#22c55e', width=2), marker=dict(size=6),
            hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Custo Líquido: €%{y:.2f}<extra></extra>'
        ))
        fig_cost.update_layout(height=350, showlegend=True, xaxis_title="Data", yaxis_title="Custo (€)",
                               plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Segoe UI", size=12),
                               margin=dict(l=0, r=0, t=20, b=0), transition_duration=1000) # Animação
        fig_cost.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
        fig_cost.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
        st.plotly_chart(fig_cost, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Análise de Cobertura Solar</div>', unsafe_allow_html=True)
        df_filtered['coverage_pct'] = (df_filtered['solar_generation'] / df_filtered['enel_consumption']) * 100
        df_filtered['coverage_pct'] = df_filtered['coverage_pct'].clip(upper=100)
        fig_coverage = go.Figure()
        fig_coverage.add_trace(go.Scatter(
            x=df_filtered['date'], y=df_filtered['coverage_pct'], mode='lines+markers', name='Percentual de Cobertura Solar',
            line=dict(color='#3b82f6', width=2), marker=dict(size=6), fill='tozeroy',
            hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Cobertura: %{y:.1f}%<extra></extra>'
        ))
        fig_coverage.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="100% Cobertura", annotation_position="top right")
        fig_coverage.update_layout(height=350, showlegend=True, xaxis_title="Data", yaxis_title="Cobertura (%)",
                                   plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Segoe UI", size=12),
                                   margin=dict(l=0, r=0, t=20, b=0), transition_duration=1000) # Animação
        fig_coverage.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
        fig_coverage.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9', range=[0, 110])
        st.plotly_chart(fig_coverage, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def display_monthly_charts(df_filtered):
    """Exibe gráficos mensais de energia e custo."""
    monthly_df = df_filtered.groupby('month_num').agg({
        'solar_generation': 'sum', 'enel_consumption': 'sum', 'enel_cost': 'sum',
        'solar_savings': 'sum', 'net_cost': 'sum', 'month': 'first'
    }).reset_index().sort_values('month_num')

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Comparação Mensal de Energia (Consumo vs. Geração)</div>', unsafe_allow_html=True)
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(
        x=monthly_df['month'], y=monthly_df['solar_generation'], name='Geração Solar', marker_color='#22c55e',
        hovertemplate='<b>%{x}</b><br>Solar: %{y:.1f} kWh<extra></extra>'
    ))
    fig_monthly.add_trace(go.Bar(
        x=monthly_df['month'], y=monthly_df['enel_consumption'], name='Consumo ENEL', marker_color='#ef4444',
        hovertemplate='<b>%{x}</b><br>ENEL: %{y:.1f} kWh<extra></extra>'
    ))
    fig_monthly.update_layout(height=400, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                              xaxis_title="Mês", yaxis_title="Energia (kWh)", plot_bgcolor='white', paper_bgcolor='white',
                              font=dict(family="Segoe UI", size=12), margin=dict(l=0, r=0, t=40, b=0),
                              transition_duration=1000) # Animação
    fig_monthly.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    fig_monthly.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_summary_table(df_filtered):
    """Exibe a tabela de resumo detalhada."""
    total_solar_generation = df_filtered['solar_generation'].sum()
    total_enel_consumption = df_filtered['enel_consumption'].sum()
    total_enel_cost = df_filtered['enel_cost'].sum()
    total_solar_savings = df_filtered['solar_savings'].sum()
    total_net_cost = df_filtered['net_cost'].sum()

    coverage_percentage = (total_solar_generation / total_enel_consumption) * 100 if total_enel_consumption > 0 else 0
    savings_vs_enel_only_pct = (total_solar_savings / total_enel_cost) * 100 if total_enel_cost > 0 else 0

    summary_data = {
        'Métrica': [
            'Geração Solar Total (kWh)', 'Consumo ENEL Total (kWh)', 'Cobertura Solar (%)',
            'Custo ENEL Original (€)', 'Economia Solar Total (€)', 'Custo Líquido com Solar (€)',
            'Economia vs Custo ENEL Original (€)', 'Geração Diária Média (kWh)', 'Consumo Diário Médio (kWh)'
        ],
        'Valor': [
            f"{total_solar_generation:.1f}", f"{total_enel_consumption:.1f}", f"{coverage_percentage:.1f}%",
            f"€{total_enel_cost:.2f}", f"€{total_solar_savings:.2f}", f"€{total_net_cost:.2f}",
            f"€{total_enel_cost - total_net_cost:.2f}",
            f"{total_solar_generation/len(df_filtered):.1f}" if len(df_filtered) > 0 else "0.0",
            f"{total_enel_consumption/len(df_filtered):.1f}" if len(df_filtered) > 0 else "0.0"
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Resumo Detalhado da Análise</div>', unsafe_allow_html=True)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


# --- Lógica da Página do Cliente ---
CLIENT_ID = '64286102' # Define o ID do cliente para esta página
CLIENT_NAME = 'Unidade Beneficiária' # Nome da unidade

st.markdown(f'<h1 class="main-header">Análise de Energia para a {CLIENT_NAME}, N° de Cliente {CLIENT_ID}</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Detalhes de consumo e geração de energia</p>', unsafe_allow_html=True)

# --- Funções para esta página específica (se necessário) ---
def generate_daily_consumption_for_chart_client(start_date_str, end_date_str, total_kwh, seed=None):
    """
    Gera dados diários de consumo para um período específico,
    distribuindo o total de kWh de forma realista.
    """
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    num_days = len(date_range)

    if seed is not None:
        np.random.seed(seed)
    daily_variations = np.random.rand(num_days) + 0.5 # Valores entre 0.5 e 1.5 para evitar zeros
    daily_variations = daily_variations / daily_variations.sum() # Normalizar para que a soma seja 1

    daily_consumption = daily_variations * total_kwh

    df_chart = pd.DataFrame({
        'Data': date_range,
        'Consumo (kWh)': daily_consumption.round(1)
    })
    return df_chart

def load_usina_4_data(file_path_usina4, start_date_str, end_date_str):
    """
    Carrega dados de geração de energia do arquivo canamary-usina-4.xlsx - Sheet1.csv,
    converte de Watts para kWh e filtra pelo período de leitura.
    """
    try:
        df = pd.read_csv(file_path_usina4, delimiter=',') # Assumindo que este CSV usa ',' como delimitador
        df = df.rename(columns={"Updated Time": "Data", "Production Power(W)": "Producao_W"})

        # Converter 'Data' para datetime, tratando possíveis erros
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data'])

        # Converter 'Producao_W' para numérico, tratando 'nan' ou strings vazias
        df['Producao_W'] = pd.to_numeric(df['Producao_W'], errors='coerce').fillna(0)

        # Converter Watts para kWh (W * 5min / 60min/h / 1000W/kW)
        # Cada linha é um intervalo de 5 minutos, então (W * 5/60) / 1000 = kWh
        df['Geração (kWh)'] = (df['Producao_W'] * 5 / 60) / 1000

        # Agrupar por dia para obter a geração diária total
        daily_df = df.groupby(df['Data'].dt.date)['Geração (kWh)'].sum().reset_index()
        daily_df['Data'] = pd.to_datetime(daily_df['Data']) # Converter de volta para datetime para filtragem

        # Filtrar pelo período de leitura
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        filtered_df = daily_df[(daily_df['Data'] >= start_date) & (daily_df['Data'] <= end_date)]

        return filtered_df
    except FileNotFoundError as e:
        st.error(f"Erro: Arquivo CSV não encontrado. Por favor, certifique-se de que '{e.filename}' está no diretório correto do seu aplicativo.")
        return pd.DataFrame({'Data': [], 'Geração (kWh)': []}) # Retorna DataFrame vazio em caso de erro
    except Exception as e:
        st.error(f"Erro ao processar arquivos CSV de geração da usina: {e}")
        return pd.DataFrame({'Data': [], 'Geração (kWh)': []}) # Retorna DataFrame vazio em caso de erro


# Verifica se os dados globais foram carregados pelo dashboard.py
if st.session_state.all_clients_data.empty:
    st.info("Por favor, carregue ou gere os dados de energia na página principal para ver a análise do cliente. Navegue de volta para 'MMC Soluções'.")
    st.stop() # Para a execução desta página se os dados não estiverem disponíveis

# Se os dados estiverem disponíveis, continue com a lógica da página
df_client_all_data = st.session_state.all_clients_data[st.session_state.all_clients_data['client_id'] == CLIENT_ID]

# --- Dados específicos para o cliente 64286102 ---
start_read_date = '2025-06-25' # Data de início da leitura
end_read_date = '2025-07-18'  # Data de fim da leitura
system_type = 'TRIFÁSICO'
total_consumption_kwh = 494.0
plant_name = 'Usina 1' # De acordo com o prompt, esta unidade é atendida pela Usina 1

# --- Primeiro Gráfico: Consumo ENEL Mensal (Simulado diariamente para o período) ---
daily_consumption_data = generate_daily_consumption_for_chart_client(
    start_read_date, end_read_date, total_consumption_kwh, seed=int(CLIENT_ID)
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown(f'<div class="chart-title-highlight">Consumo ENEL Mensal <br> N° de Cliente {CLIENT_ID}</div>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; color: #64748b; margin-top: -0.5rem; margin-bottom: 0.5rem;">Sistema: {system_type} | Período: {datetime.strptime(start_read_date, "%Y-%m-%d").strftime("%d/%m/%Y")} a {datetime.strptime(end_read_date, "%Y-%m-%d").strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

fig_enel_consumption = go.Figure()
fig_enel_consumption.add_trace(go.Bar(
    x=daily_consumption_data['Data'],
    y=daily_consumption_data['Consumo (kWh)'],
    name='Consumo Diário ENEL',
    marker_color='#ef4444', # Vermelho para consumo ENEL
    hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Consumo: %{y:.1f} kWh<extra></extra>'
))
fig_enel_consumption.update_layout(
    height=350, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_title="Dia do Mês", yaxis_title="Consumo (kWh)", hovermode='x unified', plot_bgcolor='white',
    paper_bgcolor='white', font=dict(family="Segoe UI", size=12), margin=dict(l=0, r=0, t=40, b=0),
    transition_duration=1000
)
fig_enel_consumption.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9', tickformat="%d/%m")
fig_enel_consumption.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
st.plotly_chart(fig_enel_consumption, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Mensagens Importantes da Conta ---
st.markdown("---")
st.markdown("### ✉️ Mensagens Importantes da Conta")
st.markdown("""
**Períodos:**
* **Band. Tarif.: Vermelha:** 26/06 - 18/07
* Bandeira vermelha patamar 1 em julho/25: as tarifas dos consumidores serão acrescidas em **R$ 4,463** a cada **100kW/h** consumidos.

**Informações de Crédito:**
* **Ener. injetada HFP no mês:** 0 kWh
* **Saldo utilizado no mês:** 309.06 kWh
* **Saldo atualizado:** 0 kWh
* **Créditos a Expirar no próximo mês:** 0 kWh
""")

# --- Segundo Gráfico: Geração de Energia da Usina 1 (Dados do canamary-usina-4.xlsx - Sheet1.csv) ---
# Caminho para o arquivo CSV (assumindo que está na raiz do repositório)
file_path_usina4_sheet1 = 'canamary-usina-4.xlsx - Sheet1.csv'

daily_generation_usina1_data = load_usina_4_data(
    file_path_usina4_sheet1, start_read_date, end_read_date
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown(f'<div class="chart-title-highlight">Geração de Energia Solar - {plant_name} (Período de Leitura)</div>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; color: #64748b; margin-top: -0.5rem; margin-bottom: 0.5rem;">Período: {datetime.strptime(start_read_date, "%Y-%m-%d").strftime("%d/%m/%Y")} a {datetime.strptime(end_read_date, "%Y-%m-%d").strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

fig_generation_client = go.Figure()
fig_generation_client.add_trace(go.Bar(
    x=daily_generation_usina1_data['Data'],
    y=daily_generation_usina1_data['Geração (kWh)'],
    name=f'Geração - {plant_name}',
    marker_color='#22c55e', # Verde para geração
    hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Geração: %{y:.1f} kWh<extra></extra>'
))
fig_generation_client.update_layout(
    height=350, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_title="Dia do Mês", yaxis_title="Geração (kWh)", hovermode='x unified', plot_bgcolor='white',
    paper_bgcolor='white', font=dict(family="Segoe UI", size=12), margin=dict(l=0, r=0, t=40, b=0),
    transition_duration=1000
)
fig_generation_client.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9', tickformat="%d/%m")
fig_generation_client.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
st.plotly_chart(fig_generation_client, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Terceiro Gráfico: Comparação de Consumo vs. Geração ---
# Merge dos dados de consumo e geração para o gráfico de comparação
comparison_df = pd.merge(
    daily_consumption_data.rename(columns={'Consumo (kWh)': 'Consumo ENEL'}),
    daily_generation_usina1_data.rename(columns={'Geração (kWh)': 'Geração Usina'}),
    on='Data',
    how='outer'
).fillna(0) # Preenche NaNs com 0 caso haja datas sem dados em um dos lados

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown(f'<div class="chart-title-highlight">Comparação: Consumo ENEL vs. Geração Solar ({plant_name})</div>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; color: #64748b; margin-top: -0.5rem; margin-bottom: 0.5rem;">Período: {datetime.strptime(start_read_date, "%Y-%m-%d").strftime("%d/%m/%Y")} a {datetime.strptime(end_read_date, "%Y-%m-%d").strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

fig_comparison = go.Figure()
fig_comparison.add_trace(go.Bar(
    x=comparison_df['Data'],
    y=comparison_df['Consumo ENEL'],
    name='Consumo ENEL',
    marker_color='#ef4444', # Vermelho
    hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Consumo: %{y:.1f} kWh<extra></extra>'
))
fig_comparison.add_trace(go.Bar(
    x=comparison_df['Data'],
    y=comparison_df['Geração Usina'],
    name='Geração Usina',
    marker_color='#22c55e', # Verde
    hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Geração: %{y:.1f} kWh<extra></extra>'
))
fig_comparison.update_layout(
    height=400, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_title="Data", yaxis_title="Energia (kWh)", hovermode='x unified', plot_bgcolor='white',
    paper_bgcolor='white', font=dict(family="Segoe UI", size=12), margin=dict(l=0, r=0, t=40, b=0),
    barmode='group', # Agrupa as barras lado a lado
    transition_duration=1000
)
fig_comparison.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9', tickformat="%d/%m")
fig_comparison.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
st.plotly_chart(fig_comparison, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- Detalhes Importantes para o Cliente Final ---
st.markdown("---")
st.markdown("### ✨ Detalhes Importantes para o Cliente")

total_consumption = daily_consumption_data['Consumo (kWh)'].sum()
total_generation = daily_generation_usina1_data['Geração (kWh)'].sum()

# A economia é o mínimo entre o consumo e a geração, pois você só economiza o que gerou e consumiu.
economy_kwh = min(total_consumption, total_generation)

# Calcular o custo total original (sem solar)
# Assumindo uma tarifa ENEL padrão para o cálculo da economia monetária
enel_rate_for_calc = 0.22 # Use a tarifa ENEL definida no dashboard.py ou um valor fixo
original_cost = total_consumption * enel_rate_for_calc

# Custo da energia economizada
saved_cost = economy_kwh * enel_rate_for_calc

st.markdown(f"""
Para a **{CLIENT_NAME}, N° de Cliente {CLIENT_ID}**, no período de **{datetime.strptime(start_read_date, "%Y-%m-%d").strftime("%d/%m/%Y")} a {datetime.strptime(end_read_date, "%Y-%m-%d").strftime("%d/%m/%Y")}**:

* **Consumo Total Registrado (ENEL):** **{total_consumption:.1f} kWh**
* **Geração Total da {plant_name}:** **{total_generation:.1f} kWh**

Com base nesses dados, a usina solar gerou **{total_generation:.1f} kWh** de energia limpa, que contribuiu para atender ao seu consumo.

**Sua Economia Potencial:**
* Você economizou o equivalente a **{economy_kwh:.1f} kWh** em energia que não precisou comprar da ENEL.
* Isso representa uma economia estimada de **€{saved_cost:.2f}** na sua conta de energia (considerando a tarifa de €{enel_rate_for_calc:.2f}/kWh).

**Próximos Passos:**
* Continue monitorando seu consumo e geração para otimizar o uso da energia solar.
* Seu saldo de créditos de energia é um ativo valioso. Acompanhe a validade dos créditos para garantir que sejam utilizados.
* Para uma análise mais aprofundada ou dúvidas sobre sua conta, entre em contato com a MMC Soluções.
""")
