# pages/4_Cliente_52764939.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

# --- Funções de Exibição de Gráficos (Reutilizáveis) ---
# Copiadas das páginas de cliente existentes para consistência.

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
CLIENT_ID = '52764939' # Define o ID do cliente para esta página
CLIENT_NAME = 'Unidade Geradora' # Nome da unidade

st.markdown(f'<h1 class="main-header">Análise de Energia para a {CLIENT_NAME}, N° de Cliente {CLIENT_ID}</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Detalhes de consumo e geração de energia</p>', unsafe_allow_html=True)

if not st.session_state.all_clients_data.empty:
    df_client = st.session_state.all_clients_data[st.session_state.all_clients_data['client_id'] == CLIENT_ID]

    if not df_client.empty:
        # Recuperar a tarifa ENEL (assumindo que está no session_state ou é um valor fixo)
        # Para este exemplo, vamos usar um valor padrão ou você pode passá-lo via session_state no dashboard.py
        enel_rate = 0.22 # Valor padrão, ajuste se necessário

        # Simular dados de consumo para este cliente (2245.00 kWh) para um período de 30 dias (Junho de 2025)
        # Como a geração ainda será inserida, vamos manter a geração solar como 0 por enquanto
        start_date_sim = datetime(2025, 6, 1)
        end_date_sim = datetime(2025, 6, 30)
        total_consumption_kwh = 2245.00

        date_range_sim = pd.date_range(start=start_date_sim, end=end_date_sim, freq='D')
        num_days_sim = len(date_range_sim)

        np.random.seed(int(CLIENT_ID)) # Seed baseada no ID do cliente para reprodutibilidade
        daily_variations = np.random.rand(num_days_sim) + 0.5 # Valores entre 0.5 e 1.5
        daily_variations = daily_variations / daily_variations.sum() # Normalizar para que a soma seja 1

        simulated_consumption = daily_variations * total_consumption_kwh
        simulated_solar_generation = np.zeros(num_days_sim) # Geração solar como 0 por enquanto

        # Criar um DataFrame para os dados simulados deste cliente
        simulated_df_client = pd.DataFrame({
            'client_id': CLIENT_ID,
            'date': date_range_sim,
            'solar_generation': simulated_solar_generation.round(1),
            'enel_consumption': simulated_consumption.round(1)
        })

        # Adicionar campos calculados (enel_cost, solar_savings, net_consumption, net_cost)
        simulated_df_client['enel_cost'] = simulated_df_client['enel_consumption'] * enel_rate
        simulated_df_client['solar_savings'] = simulated_df_client['solar_generation'] * enel_rate
        simulated_df_client['net_consumption'] = simulated_df_client['enel_consumption'] - simulated_df_client['solar_generation']
        simulated_df_client['net_cost'] = simulated_df_client['net_consumption'] * enel_rate
        simulated_df_client['net_cost'] = simulated_df_client['net_cost'].clip(lower=0)

        # Adicionar componentes de data
        simulated_df_client['day_name'] = simulated_df_client['date'].dt.strftime('%A')
        simulated_df_client['day_num'] = simulated_df_client['date'].dt.day
        simulated_df_client['month'] = simulated_df_client['date'].dt.strftime('%B')
        simulated_df_client['month_num'] = simulated_df_client['date'].dt.month

        # Usar o DataFrame simulado para exibição
        display_metrics(simulated_df_client, enel_rate)

        st.markdown("---")
        view_mode = st.radio(
            "Selecionar Visualização",
            ["Análise Diária", "Resumo Mensal"],
            index=0,
            key=f"view_mode_{CLIENT_ID}", # Chave única para este radio button
            help="Escolha entre a visualização diária ou mensal agregada dos dados."
        )

        if view_mode == 'Análise Diária':
            display_daily_charts(simulated_df_client)
        else:
            display_monthly_charts(simulated_df_client)

        display_summary_table(simulated_df_client)

    else:
        st.warning(f"⚠️ Nenhum dado disponível para o Cliente {CLIENT_ID}. Por favor, verifique a fonte de dados na página principal.")
else:
    st.info("Por favor, carregue ou gere os dados de energia na página principal para ver a análise do cliente.")
