# dashboard.py (Arquivo Principal)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import io # Para lidar com downloads de arquivos

# --- Configuração da Página e CSS ---
st.set_page_config(
    page_title="MMC Soluções", # Título da página atualizado
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# --- Inicializar variáveis de estado da sessão ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'daily'
if 'show_manual_entry' not in st.session_state:
    st.session_state.show_manual_entry = False
if 'use_sample_data' not in st.session_state:
    st.session_state.use_sample_data = False
if 'manual_data' not in st.session_state:
    st.session_state.manual_data = []
if 'all_clients_data' not in st.session_state:
    st.session_state.all_clients_data = pd.DataFrame() # DataFrame vazio para inicializar

# --- Funções de Geração de Dados (Modificadas para incluir client_id) ---

def generate_sample_data(client_ids):
    """Gera dados de amostra realistas para múltiplos clientes."""
    start_date = datetime(2025, 6, 6)
    end_date = datetime(2025, 7, 7)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    all_data = []
    for client_id in client_ids:
        np.random.seed(int(client_id) % 1000) # Seed diferente por cliente para variação

        for i, date in enumerate(date_range):
            # Base values slightly different per client
            base_solar = 230 + (int(client_id) % 50) - 25 # Variação de -25 a +24
            base_consumption = 230 + (int(client_id) % 40) - 20 # Variação de -20 a +19

            solar_variation = np.random.normal(0, 25)
            weather_factor = 0.95 if np.random.random() < 0.2 else 1.0

            consumption_variation = np.random.normal(0, 20)
            is_weekend = date.weekday() >= 5
            weekend_factor = 1.1 if is_weekend else 1.0

            solar_generation = max(180, base_solar + solar_variation * weather_factor)
            enel_consumption = max(190, base_consumption + consumption_variation * weekend_factor)

            days_from_start = (date - start_date).days
            seasonal_boost = 1 + (days_from_start / 100)
            solar_generation *= seasonal_boost

            all_data.append({
                'client_id': client_id,
                'date': date,
                'solar_generation': round(solar_generation, 1),
                'enel_consumption': round(enel_consumption, 1),
                'day_name': date.strftime('%A'),
                'day_num': date.day,
                'month': date.strftime('%B'),
                'month_num': date.month
            })
    return pd.DataFrame(all_data)

def generate_solar_data(start_date, end_date, system_size, efficiency, client_id):
    """Gera dados de geração solar realistas para um cliente específico."""
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    np.random.seed(int(client_id) + 42) # Seed diferente por cliente

    data = []
    for date in date_range:
        day_of_year = date.timetuple().tm_yday
        seasonal_factor = 0.7 + 0.3 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        weather_factor = 0.6 + 0.4 * np.random.random()

        daily_generation = system_size * 5.5 * seasonal_factor * weather_factor * (efficiency / 100)

        data.append({
            'client_id': client_id,
            'date': date,
            'solar_generation': round(daily_generation, 2),
            'day_name': date.strftime('%A'),
            'day_num': date.day,
            'month': date.strftime('%B'),
            'month_num': date.month
        })
    return pd.DataFrame(data)

def generate_enel_data(start_date, end_date, baseline_consumption, enel_rate, client_id):
    """Gera dados de consumo ENEL para um cliente específico."""
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    np.random.seed(int(client_id) + 24) # Seed diferente por cliente

    data = []
    for date in date_range:
        is_weekend = date.weekday() >= 5
        weekend_factor = 1.2 if is_weekend else 1.0

        day_of_year = date.timetuple().tm_yday
        seasonal_factor = 0.8 + 0.4 * (np.sin(2 * np.pi * (day_of_year - 80) / 365) ** 2)

        daily_variation = 0.8 + 0.4 * np.random.random()

        daily_consumption = baseline_consumption * weekend_factor * seasonal_factor * daily_variation

        data.append({
            'client_id': client_id,
            'date': date,
            'enel_consumption': round(daily_consumption, 2),
            'enel_cost': round(daily_consumption * enel_rate, 2),
            'day_name': date.strftime('%A'),
            'day_num': date.day,
            'month': date.strftime('%B'),
            'month_num': date.month
        })
    return pd.DataFrame(data)

# --- Funções de Carregamento de Dados ---

def load_file_data(uploaded_file, expected_columns):
    """Função auxiliar para carregar dados de arquivos CSV/Excel carregados."""
    if uploaded_file is None:
        return None

    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Tipo de arquivo não suportado: {uploaded_file.name}. Por favor, carregue CSV, XLS ou XLSX.")
            return None

        # Validar colunas
        if not all(col in df.columns for col in expected_columns):
            st.error(f"O arquivo carregado '{uploaded_file.name}' deve conter as colunas: {', '.join(expected_columns)}")
            return None

        # Renomear colunas para nomes padrão para processamento
        # Assumimos que a coluna de ID do cliente é 'client_id' ou a primeira coluna se não especificado
        if 'client_id' in expected_columns:
            df = df.rename(columns={expected_columns[0]: 'client_id', expected_columns[1]: 'date', expected_columns[2]: 'energy_kwh'})
        else: # Para compatibilidade com uploads antigos, assumir que client_id é adicionado manualmente ou simulado
            df = df.rename(columns={expected_columns[0]: 'date', expected_columns[1]: 'energy_kwh'})
            df['client_id'] = 'N/A' # Placeholder, será tratado no manual_data ou simulação

        # Converter coluna de data para objetos datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']) # Remover linhas onde a conversão de data falhou

        # Garantir que a coluna de energia seja numérica
        df['energy_kwh'] = pd.to_numeric(df['energy_kwh'], errors='coerce')
        df = df.dropna(subset=['energy_kwh']) # Remover linhas onde a conversão de energia falhou

        return df

    except Exception as e:
        st.error(f"Erro ao processar {uploaded_file.name}: {e}. Por favor, verifique o formato e o conteúdo do arquivo.")
        return None

def get_all_clients_combined_data(solar_file, enel_file, manual_data, data_input_method, use_sample_data,
                                  start_date, end_date, solar_system_size, efficiency_factor, baseline_consumption, enel_rate,
                                  simulated_client_ids):
    """Combina dados de várias fontes para TODOS os clientes em um único DataFrame."""
    df_all = pd.DataFrame()
    data_source_description = ""

    if data_input_method == "Carregar Dados Reais":
        # Para dados reais, esperamos que os arquivos já contenham o client_id
        solar_df = load_file_data(solar_file, ['client_id', 'date', 'solar_generation_kwh'])
        enel_df = load_file_data(enel_file, ['client_id', 'date', 'enel_consumption_kwh'])

        # Processar dados manuais se disponíveis
        manual_df = pd.DataFrame(manual_data)
        if not manual_df.empty:
            manual_df['date'] = pd.to_datetime(manual_df['date'])
            manual_solar_df = manual_df[['client_id', 'date', 'solar_generation']].rename(columns={'solar_generation': 'solar_generation_kwh'})
            manual_enel_df = manual_df[['client_id', 'date', 'enel_consumption']].rename(columns={'enel_consumption': 'enel_consumption_kwh'})

            if solar_df is None:
                solar_df = manual_solar_df
            else:
                solar_df = pd.concat([solar_df, manual_solar_df]).drop_duplicates(subset=['client_id', 'date']).sort_values('date')

            if enel_df is None:
                enel_df = manual_enel_df
            else:
                enel_df = pd.concat([enel_df, manual_enel_df]).drop_duplicates(subset=['client_id', 'date']).sort_values('date')

        if solar_df is not None and enel_df is not None and not solar_df.empty and not enel_df.empty:
            df_all = pd.merge(solar_df.rename(columns={'energy_kwh': 'solar_generation'}),
                              enel_df.rename(columns={'energy_kwh': 'enel_consumption'}),
                              on=['client_id', 'date'],
                              how='outer')
            df_all = df_all.dropna()
            if not df_all.empty:
                data_source_description = f"Dados Reais ({len(df_all['client_id'].unique())} clientes, {len(df_all)} dias)"
        elif not manual_df.empty:
            df_all = manual_df.copy()
            df_all['date'] = pd.to_datetime(df_all['date'])
            df_all = df_all.rename(columns={'solar_generation': 'solar_generation', 'enel_consumption': 'enel_consumption'})
            data_source_description = f"Dados Manuais ({len(df_all['client_id'].unique())} clientes, {len(df_all)} dias)"
        else:
            return pd.DataFrame(), ""

    elif data_input_method == "Usar Dados Simulados":
        if use_sample_data:
            df_all = generate_sample_data(simulated_client_ids)
            data_source_description = f"Dados de Amostra ({len(simulated_client_ids)} clientes)"
        else:
            # Gerar dados simulados para cada cliente selecionado
            all_solar_dfs = []
            all_enel_dfs = []
            for client_id in simulated_client_ids:
                all_solar_dfs.append(generate_solar_data(start_date, end_date, solar_system_size, efficiency_factor, client_id))
                all_enel_dfs.append(generate_enel_data(start_date, end_date, baseline_consumption, enel_rate, client_id))

            solar_sim_df_all = pd.concat(all_solar_dfs)
            enel_sim_df_all = pd.concat(all_enel_dfs)

            df_all = pd.merge(solar_sim_df_all, enel_sim_df_all, on=['client_id', 'date', 'day_name', 'day_num', 'month', 'month_num'])
            data_source_description = f"Dados Simulados ({len(simulated_client_ids)} clientes)"

    if not df_all.empty:
        df_all['enel_cost'] = df_all['enel_consumption'] * enel_rate
        df_all['solar_savings'] = df_all['solar_generation'] * enel_rate
        df_all['net_consumption'] = df_all['enel_consumption'] - df_all['solar_generation']
        df_all['net_cost'] = df_all['net_consumption'] * enel_rate
        df_all['net_cost'] = df_all['net_cost'].clip(lower=0)

        df_all['day_name'] = df_all['date'].dt.strftime('%A')
        df_all['day_num'] = df_all['date'].dt.day
        df_all['month'] = df_all['date'].dt.strftime('%B')
        df_all['month_num'] = df_all['date'].dt.month
        df_all = df_all.sort_values(['client_id', 'date']).reset_index(drop=True)

    return df_all, data_source_description

# --- Cabeçalho da Página Principal ---
st.markdown('<h1 class="main-header">MMC Soluções</h1>', unsafe_allow_html=True) # Título principal atualizado
st.markdown('<p class="sub-header">Painel de análise de consumo e geração de energia para múltiplos clientes</p>', unsafe_allow_html=True) # Subtítulo atualizado

# --- Sidebar para Configuração de Dados ---
with st.sidebar:
    st.markdown("### ⚙️ Configuração de Dados")
    st.markdown("---")

    data_input_method = st.radio(
        "Escolha a fonte de dados:",
        ["Carregar Dados Reais", "Usar Dados Simulados"],
        index=0,
        help="Carregue seus dados reais ou use dados simulados para teste"
    )

    st.markdown("---")

    # Inicialização padrão para variáveis que podem não ser definidas em todos os ramos
    solar_file = None
    enel_file = None
    start_date = datetime(2024, 6, 6)
    end_date = datetime(2024, 7, 7)
    solar_system_size = 8.5
    efficiency_factor = 85
    baseline_consumption = 25
    enel_rate = 0.22
    simulated_client_ids = ['5634057', '52764939'] # IDs padrão para simulação

    if data_input_method == "Carregar Dados Reais":
        st.markdown("**📁 Carregue Seus Dados**")

        solar_file = st.file_uploader(
            "Carregar Dados Solares",
            type=['csv', 'xlsx', 'xls'],
            help="Arquivo com as colunas: client_id, date (AAAA-MM-DD), solar_generation_kwh",
            key="solar_upload"
        )
        enel_file = st.file_uploader(
            "Carregar Dados ENEL",
            type=['csv', 'xlsx', 'xls'],
            help="Arquivo com as colunas: client_id, date (AAAA-MM-DD), enel_consumption_kwh",
            key="enel_upload"
        )

        st.markdown("---")
        st.markdown("**✏️ Ou Insira Dados Manualmente**")
        if st.button("📝 Alternar Entrada Manual de Dados"):
            st.session_state.show_manual_entry = not st.session_state.show_manual_entry

        if st.session_state.show_manual_entry:
            st.markdown("*Adicionar Nova Entrada Manual*")
            manual_client_id = st.text_input("ID do Cliente", value="NOVO_CLIENTE", key="manual_client_id_input")
            manual_date = st.date_input("Data", value=datetime.now().date(), key="manual_date_input")
            manual_solar = st.number_input("Geração Solar (kWh)", min_value=0.0, max_value=1000.0, value=0.0, step=0.1, key="manual_solar_input")
            manual_enel = st.number_input("Consumo ENEL (kWh)", min_value=0.0, max_value=1000.0, value=0.0, step=0.1, key="manual_enel_input")

            col_manual_add, col_manual_clear = st.columns(2)
            with col_manual_add:
                if st.button("➕ Adicionar Entrada"):
                    new_entry_date_str = manual_date.strftime('%Y-%m-%d')
                    if any(e['client_id'] == manual_client_id and e['date'] == new_entry_date_str for e in st.session_state.manual_data):
                        st.warning(f"Entrada para Cliente {manual_client_id} na data {new_entry_date_str} já existe.")
                    else:
                        st.session_state.manual_data.append({
                            'client_id': manual_client_id,
                            'date': new_entry_date_str,
                            'solar_generation': manual_solar,
                            'enel_consumption': manual_enel
                        })
                        st.success("✅ Entrada adicionada!")
            with col_manual_clear:
                if st.button("🗑️ Limpar Todos os Dados Manuais"):
                    st.session_state.manual_data = []
                    st.success("✅ Dados manuais limpos!")

            if st.session_state.get('manual_data'):
                st.markdown("*Entradas Manuais Atuais:*")
                manual_df_display = pd.DataFrame(st.session_state.manual_data)
                st.dataframe(manual_df_display, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma entrada manual ainda.")

    else: # Usar Dados Simulados
        st.markdown("**📅 Opções de Dados Simulados**")
        st.session_state.use_sample_data = st.checkbox(
            "📊 Usar Dados de Amostra (Período Fixo, ~230 kWh/dia)",
            value=st.session_state.use_sample_data,
            help="Usa um conjunto de dados predefinido para os clientes 5634057 e 52764939."
        )

        if not st.session_state.use_sample_data:
            st.markdown("**⚙️ Configurações de Simulação**")
            simulated_client_ids = st.multiselect(
                "Selecionar IDs de Clientes para Simulação",
                options=['5634057', '52764939', '12345678', '98765432'], # Mais IDs para escolha
                default=['5634057', '52764939'],
                help="Escolha quais clientes terão dados simulados gerados."
            )
            start_date = st.date_input("Data de Início", value=datetime(2024, 6, 6), help="Início do período de simulação.")
            end_date = st.date_input("Data de Fim", value=datetime(2024, 7, 7), help="Fim do período de simulação.")
            solar_system_size = st.number_input("Tamanho do Sistema Solar (kWp)", min_value=1.0, max_value=50.0, value=8.5, step=0.5, help="Capacidade de pico do sistema solar.")
            efficiency_factor = st.number_input("Eficiência do Sistema (%)", min_value=70, max_value=95, value=85, step=1, help="Eficiência geral do sistema.")
            baseline_consumption = st.number_input("Consumo Diário Base (kWh)", min_value=10, max_value=100, value=25, step=1, help="Consumo diário médio sem solar.")
        else: # Para dados de amostra, os IDs são fixos
            simulated_client_ids = ['5634057', '52764939']
            st.info(f"Dados de amostra gerados para os clientes: {', '.join(simulated_client_ids)}")

    st.markdown("---")
    enel_rate = st.number_input("Tarifa ENEL (€/kWh)", min_value=0.01, max_value=1.0, value=0.22, step=0.01, help="Tarifa atual de eletricidade da ENEL.")
    st.markdown("---")

# --- Carregar/Gerar e Armazenar Dados para TODOS os clientes ---
# Isso é feito APENAS UMA VEZ por execução completa do script, ou quando as entradas mudam.
st.session_state.all_clients_data, data_source_description = get_all_clients_combined_data(
    solar_file, enel_file, st.session_state.manual_data, data_input_method, st.session_state.use_sample_data,
    start_date, end_date, solar_system_size, efficiency_factor, baseline_consumption, enel_rate,
    simulated_client_ids
)

# --- Conteúdo da Página Principal (Visão Geral) ---
if not st.session_state.all_clients_data.empty:
    num_clientes = len(st.session_state.all_clients_data['client_id'].unique())
    st.markdown(f"**Número de Clientes Disponíveis: {num_clientes}**")
    st.markdown(f"Período Analisado: {st.session_state.all_clients_data['date'].min().strftime('%d-%m-%Y')} a {st.session_state.all_clients_data['date'].max().strftime('%d-%m-%Y')}")
else:
    # --- Seção: Outras Unidades e Clientes (Movida para o topo) ---
    st.markdown("---")
    st.markdown("### 🔍 Outras Unidades e Clientes")
    st.markdown('<p style="text-align: center; color: #64748b; margin-bottom: 1rem;">Clique nos botões abaixo para visualizar análises detalhadas de outras unidades. A navegação completa está disponível na barra lateral.</p>', unsafe_allow_html=True)

    col_unit1, col_unit2 = st.columns(2)

    with col_unit1:
        st.markdown(f"""
        <a href="#" class="unit-button">
            Unidade Geradora<br>N° de Cliente 52764939
        </a>
        """, unsafe_allow_html=True)

    with col_unit2:
        st.markdown(f"""
        <a href="#" class="unit-button">
            Unidade Beneficiária<br>N° de Cliente 56340547
        </a>
        """, unsafe_allow_html=True)
    st.markdown("---") # Separador após os botões

    st.markdown("### 🧾 Conta Mais Recente") # Título da seção atualizado para "Conta Mais Recente"
    st.warning("⚠️ Existem novas contas para serem visualizadas!") # Aviso de novas contas

    # --- Gráfico de Consumo da Conta Mais Recente (Cliente 64286102) ---
    def generate_daily_consumption_for_chart(start_date_str, end_date_str, total_kwh):
        """
        Gera dados diários de consumo para um período específico,
        distribuindo o total de kWh de forma realista.
        """
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        num_days = len(date_range)

        np.random.seed(64286102) # Seed baseada no ID do cliente
        daily_variations = np.random.rand(num_days) + 0.5 # Valores entre 0.5 e 1.5 para evitar zeros
        daily_variations = daily_variations / daily_variations.sum() # Normalizar para que a soma seja 1

        daily_consumption = daily_variations * total_kwh

        df_chart = pd.DataFrame({
            'Data': date_range,
            'Consumo (kWh)': daily_consumption.round(1)
        })
        return df_chart

    # --- Gráfico de Geração de Energia (Simulado com base nos arquivos anexados) ---
    def generate_daily_energy_generation_from_monthly(start_date_str, end_date_str, monthly_totals_kwh, seed_offset=0):
        """
        Gera dados diários de geração de energia para um período específico,
        distribuindo os totais mensais de forma realista.

        monthly_totals_kwh: dict, e.g., { (2025, 6): 4786.3, (2025, 7): 3763.4 }
        seed_offset: int, para gerar variações diferentes para cada usina
        """
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')

        daily_data = []
        np.random.seed(int(start_date.strftime('%Y%m%d')) + seed_offset) # Seed para reprodutibilidade

        for date in date_range:
            year = date.year
            month = date.month

            monthly_total = monthly_totals_kwh.get((year, month), 0)
            num_days_in_month = calendar.monthrange(year, month)[1]

            if monthly_total > 0:
                base_daily_avg = monthly_total / num_days_in_month
                daily_variation_factor = 0.8 + 0.4 * np.random.rand() # Factor between 0.8 and 1.2
                daily_gen = base_daily_avg * daily_variation_factor
                daily_gen = max(0, daily_gen) # Ensure no negative generation

                daily_data.append({
                    'Data': date,
                    'Geração (kWh)': round(daily_gen, 1) # Corrigido: usar round() embutido
                })
            else:
                daily_data.append({
                    'Data': date,
                    'Geração (kWh)': 0.0
                })

        return pd.DataFrame(daily_data)


    # Dados para o gráfico de Consumo: Cliente 64286102
    client_id_consumption_chart = '64286102'
    meter_number = '6522800-ELE-647'
    start_read_date_consumption = '2025-06-26'
    end_read_date_consumption = '2025-07-18'
    total_consumption_kwh = 494.0

    daily_consumption_chart_data = generate_daily_consumption_for_chart(
        start_read_date_consumption, end_read_date_consumption, total_consumption_kwh
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title-highlight">Unidade Beneficiária, N° de Cliente {client_id_consumption_chart} <br> (Conta Mais Recente)</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #64748b; margin-top: -0.5rem; margin-bottom: 0.5rem;">N° de Medidor: {meter_number} | Período: {datetime.strptime(start_read_date_consumption, "%Y-%m-%d").strftime("%d/%m/%Y")} a {datetime.strptime(end_read_date_consumption, "%Y-%m-%d").strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)


    fig_consumption_daily = go.Figure()
    fig_consumption_daily.add_trace(go.Bar(
        x=daily_consumption_chart_data['Data'],
        y=daily_consumption_chart_data['Consumo (kWh)'],
        name='Consumo Diário',
        marker_color='#3b82f6', # Azul para consumo
        hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Consumo: %{y:.1f} kWh<extra></extra>'
    ))

    fig_consumption_daily.update_layout(
        height=350, # Reduzido
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_title="Dia do Mês",
        yaxis_title="Consumo (kWh)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=12),
        margin=dict(l=0, r=0, t=40, b=0),
        transition_duration=1000 # Animação de 1 segundo
    )

    fig_consumption_daily.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9', tickformat="%d/%m")
    fig_consumption_daily.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')

    st.plotly_chart(fig_consumption_daily, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SEGUNDO GRÁFICO: Geração de Energia no mesmo período (Múltiplas Usinas) ---
    # Dados de geração mensal da Usina Original (report-1.xls e report-2.xls)
    monthly_generation_original_plant = {
        (2025, 6): 4786.3, # "Energy this Month(kWh)" from report-1.xls for June 2025
        (2025, 7): 3763.4  # "Energy this Month(kWh)" from report-2.xls for July 2025
    }
    # Dados de geração mensal da Usina Maracanaú (report-06.xls e report-07.xls)
    monthly_generation_maracanau_plant = {
        (2025, 6): 8094.0, # "Energy this Month(kWh)" from report-06.xls for June 2025
        (2025, 7): 6529.3  # "Energy this Month(kWh)" from report-07.xls for July 2025
    }

    daily_generation_original_plant_data = generate_daily_energy_generation_from_monthly(
        start_read_date_consumption, end_read_date_consumption, monthly_generation_original_plant, seed_offset=1
    )
    daily_generation_maracanau_plant_data = generate_daily_energy_generation_from_monthly(
        start_read_date_consumption, end_read_date_consumption, monthly_generation_maracanau_plant, seed_offset=2
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title-highlight">Geração de Energia Solar (Período de Leitura)</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #64748b; margin-top: -0.5rem; margin-bottom: 0.5rem;">Período: {datetime.strptime(start_read_date_consumption, "%Y-%m-%d").strftime("%d/%m/%Y")} a {datetime.strptime(end_read_date_consumption, "%Y-%m-%d").strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

    fig_generation_daily = go.Figure()
    fig_generation_daily.add_trace(go.Bar(
        x=daily_generation_original_plant_data['Data'],
        y=daily_generation_original_plant_data['Geração (kWh)'],
        name='Geração - Usina Original',
        marker_color='#22c55e', # Verde para geração
        hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Usina Original: %{y:.1f} kWh<extra></extra>'
    ))
    fig_generation_daily.add_trace(go.Bar(
        x=daily_generation_maracanau_plant_data['Data'],
        y=daily_generation_maracanau_plant_data['Geração (kWh)'],
        name='Geração - Usina Maracanaú',
        marker_color='#FFD700', # Dourado para outra usina
        hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Usina Maracanaú: %{y:.1f} kWh<extra></extra>'
    ))

    fig_generation_daily.update_layout(
        height=350, # Reduzido
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_title="Dia do Mês",
        yaxis_title="Geração (kWh)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=12),
        margin=dict(l=0, r=0, t=40, b=0),
        barmode='group', # Agrupa as barras lado a lado
        transition_duration=1000 # Animação de 1 segundo
    )

    fig_generation_daily.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9', tickformat="%d/%m")
    fig_generation_daily.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')

    st.plotly_chart(fig_generation_daily, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Análise e Observações (Mais breve e focada na economia) ---
    st.markdown("---")
    st.markdown("### 📈 Análise e Observações")
    total_simulated_consumption = daily_consumption_chart_data['Consumo (kWh)'].sum()
    total_simulated_generation_original = daily_generation_original_plant_data['Geração (kWh)'].sum()
    total_simulated_generation_maracanau = daily_generation_maracanau_plant_data['Geração (kWh)'].sum()
    total_combined_generation = total_simulated_generation_original + total_simulated_generation_maracanau

    # Calcular economia: o mínimo entre o consumo e a geração combinada
    economy_kwh = min(total_simulated_consumption, total_combined_generation)

    st.markdown(f"""
    Para a **Unidade Beneficiária, N° de Cliente {client_id_consumption_chart}**, no período de **{datetime.strptime(start_read_date_consumption, "%Y-%m-%d").strftime("%d/%m/%Y")} a {datetime.strptime(end_read_date_consumption, "%Y-%m-%d").strftime("%d/%m/%Y")}**:

    * **Consumo Total (Baseado em Dados Reais da ENEL):** {total_simulated_consumption:.1f} kWh
    * **Geração Solar Total Combinada (Baseado em Dados Reais de Usinas):** {total_combined_generation:.1f} kWh
        * Usina Original: {total_simulated_generation_original:.1f} kWh
        * Usina Maracanaú: {total_simulated_generation_maracanau:.1f} kWh

    A economia potencial para este cliente, utilizando a energia gerada pelas usinas, é de aproximadamente **{economy_kwh:.1f} kWh**.

    **Nota sobre os Dados:** Os valores totais de consumo e geração são provenientes de contas reais da ENEL e sites das geradoras. A distribuição diária apresentada nos gráficos é uma simulação para fins de visualização, baseada nesses totais.
    """)

    st.stop() # Parar a execução se não houver dados para análise detalhada

# --- Rodapé ---
st.markdown("---")
st.markdown("**📊 Painel de Análise Profissional de Energia** | Construído com Streamlit & Plotly")
