import streamlit as st
from pathlib import Path
import pandas as pd
from datetime import datetime
from modules.conexao_google import obter_ultima_atualizacao

from config import NOME_SISTEMA, NOME_MODULO, COLUNA_DS
from modules.educacao_permanente import (
    carregar_dados,
    exibir_grade_atividades
)
from modules.filtros_territoriais import (
    carregar_base_territorial,
    listar_distritos,
    listar_unidades,
    listar_equipes
)


# ============================================================
# 1. CONFIGURAÇÕES GERAIS
# ============================================================

st.set_page_config(
    page_title=f"{NOME_SISTEMA} | {NOME_MODULO}",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
PASTA_LOGOS = BASE_DIR / "assets" / "logos"
CSS_PATH = BASE_DIR / "assets" / "styles" / "style.css"


# ============================================================
# 2. CARREGAMENTO DA IDENTIDADE VISUAL
# ============================================================

if CSS_PATH.exists():
    with open(CSS_PATH, encoding="utf-8") as arquivo:
        st.markdown(
            f"<style>{arquivo.read()}</style>",
            unsafe_allow_html=True
        )


# ============================================================
# 3. MENU LATERAL E NAVEGAÇÃO
# ============================================================

MODULOS = [
    "Prontuário",
    "Integra.ai",
    "Fale com sua equipe",
    "Agendamento Online",
    "Agendamento Online (SSAC)",
    "Agendamentos Frustrados",
    "Jornada Digital",
    "Telessaúde",
    "Educação Permanente",
    "Ferramentas",
    "KPI's"
]

if "menu_modulos" not in st.session_state:
    st.session_state.menu_modulos = "Educação Permanente"


with st.sidebar:

    st.title("Painel CTDS")
    st.divider()

    # 3.1. Aparência dos botões do menu
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] div.stButton > button {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            width: 100% !important;
            height: 34px !important;
            min-height: 34px !important;
            padding: 5px 12px !important;
            margin: 0 !important;
            border-radius: 6px !important;
            box-shadow: none !important;
            text-align: left !important;
        }

        section[data-testid="stSidebar"] div.stButton > button > div {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            width: 100% !important;
        }

        section[data-testid="stSidebar"] div.stButton > button p {
            width: 100% !important;
            margin: 0 !important;
            text-align: left !important;
            font-size: 14px !important;
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
            background-color: #FFFFFF !important;
            color: #173568 !important;
            border: 1px solid #FFFFFF !important;
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p {
            color: #173568 !important;
            font-weight: 700 !important;
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
            background-color: transparent !important;
            color: #FFFFFF !important;
            border: 1px solid transparent !important;
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] p {
            color: #FFFFFF !important;
            font-weight: 400 !important;
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
            background-color: #42638F !important;
            border: 1px solid #42638F !important;
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover p {
            color: #FFFFFF !important;
        }

        /* Painel off-white das marcas institucionais */
        .st-key-logos_institucionais {
            background-color: #F4F0E8;
            border-radius: 14px;
            padding: 16px 12px;
            margin-top: 12px;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 3.2. Navegação entre os módulos
    with st.container(gap=0):
        for modulo in MODULOS:
            selecionado = st.session_state.menu_modulos == modulo

            st.button(
                modulo,
                key=f"nav_{modulo}",
                type="primary" if selecionado else "secondary",
                use_container_width=True,
                on_click=lambda m=modulo: st.session_state.update(
                    menu_modulos=m
                )
            )

    # 3.3. Logos institucionais
    st.divider()

    with st.container(key="logos_institucionais"):

        # Prefeitura do Recife — nova versão azul com fundo transparente
        col_esq, col_centro, col_dir = st.columns([0.1, 0.8, 0.1])
        with col_centro:
            st.image(
                str(PASTA_LOGOS / "logo_prefeitura_recife.png"),
                width=160 
            )

        # Saúde Digital Recife
        col_esq, col_centro, col_dir = st.columns([0.1, 0.8, 0.1])
        with col_centro:
            st.image(
                str(PASTA_LOGOS / "logo_saude_digital_recife_.png"),
                width=210
            )

        # Transformação Digital em Saúde
        col_esq, col_centro, col_dir = st.columns([0.1, 0.8, 0.1])
        with col_centro:
            st.image(
                str(PASTA_LOGOS / "logo_transformacao_digital_saude.png"),
                width=210
            )

    st.caption("Secretaria de Saúde Digital | Recife")


# ============================================================
# 4. CONTROLE DA NAVEGAÇÃO ENTRE MÓDULOS
# ============================================================

modulo_selecionado = st.session_state.menu_modulos

if modulo_selecionado != "Educação Permanente":
    st.info(
        f"O módulo {modulo_selecionado} será disponibilizado "
        "em uma próxima etapa."
    )
    st.stop()


# ============================================================
# 5. CABEÇALHO DO MÓDULO
# ============================================================

st.title("Educação Permanente")
st.markdown(
    "Acompanhamento dos indicadores de realização das atividades."
)
st.divider()



# ============================================================
# 6. CARREGAMENTO DAS BASES DE DADOS
# ============================================================

try:
    df = carregar_dados()
    base_territorial = carregar_base_territorial()

    if df is None:
        st.error(
            "Planilha Sala de Situação.xlsx não encontrada "
            "na pasta data."
        )
        st.stop()

    # ========================================================
    # 7. FILTROS DE CONSULTA
    # ========================================================

    col_filtros_titulo, col_atualizacao = st.columns([3, 1])

    with col_filtros_titulo:
        st.subheader("Filtros de consulta")

    with col_atualizacao:
        try:
            ultima_atualizacao = obter_ultima_atualizacao()

            if ultima_atualizacao:
                data_utc = datetime.fromisoformat(
                    ultima_atualizacao.replace("Z", "+00:00")
                )
                data_local = data_utc.astimezone()
                data_formatada = data_local.strftime(
                    "%d/%m/%Y às %H:%M"
                )
            else:
                data_formatada = "Não disponível"

        except Exception:
            data_formatada = "Não foi possível consultar"

        st.markdown(
            f"""
            <div style="
                text-align: right;
                color: #777777;
                font-size: 12px;
                line-height: 1.8;
                padding-top: 8px;
                white-space: nowrap;
            ">
                <div><b>Última atualização:</b> {data_formatada}</div>
                <div><b>Fonte:</b> Google Sheets</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    col_ds, col_unidade, col_equipe = st.columns(3)

    # Distrito Sanitário
    distritos = ["Todos"] + listar_distritos(base_territorial)

    with col_ds:
        distrito_selecionado = st.selectbox(
            "Distrito Sanitário",
            options=distritos,
            format_func=lambda x: (
                "Todos os distritos"
                if x == "Todos"
                else f"DS {x}"
            ),
            key="filtro_distrito"
        )

    # Unidade de Saúde
    unidades = listar_unidades(
        base_territorial,
        distrito_selecionado
    )

    opcoes_unidades = (
        ["Todas"]
        + unidades["Unidade"].dropna().unique().tolist()
    )

    with col_unidade:
        unidade_selecionada = st.selectbox(
            "Unidade de Saúde",
            options=opcoes_unidades,
            key="filtro_unidade"
        )

    # Equipe
    equipes = listar_equipes(
        base_territorial,
        distrito_selecionado,
        unidade_selecionada
    )

    opcoes_equipes = (
        ["Todas"]
        + equipes["Equipe"].dropna().unique().tolist()
    )

    with col_equipe:
        equipe_selecionada = st.selectbox(
            "Equipe",
            options=opcoes_equipes,
            key="filtro_equipe"
        )

    st.divider()

    # ========================================================
    # 8. APLICAÇÃO DO FILTRO DE DISTRITO
    # ========================================================

    indice_ds = ord(COLUNA_DS.upper()) - ord("A")
    df_filtrado = df.copy()

    if distrito_selecionado != "Todos":
        df_filtrado = df_filtrado[
            pd.to_numeric(
                df_filtrado.iloc[:, indice_ds],
                errors="coerce"
            ) == int(distrito_selecionado)
        ].copy()

    # ========================================================
    # 9. AVISO SOBRE UNIDADE E EQUIPE
    # ========================================================

    if (
        unidade_selecionada != "Todas"
        or equipe_selecionada != "Todas"
    ):
        st.info(
            "Unidade e Equipe estão sendo selecionadas a partir "
            "do cadastro territorial. Para filtrar os indicadores "
            "por esses campos, precisamos relacionar CNES ou INE "
            "aos registros da planilha de atividades."
        )

    # ========================================================
    # 10. EXIBIÇÃO DOS CARDS DE INDICADORES
    # ========================================================

    exibir_grade_atividades(df_filtrado)

except Exception as erro:
    st.error(f"Não foi possível carregar o painel: {erro}")
    st.exception(erro)
