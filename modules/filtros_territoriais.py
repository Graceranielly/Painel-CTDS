
import streamlit as st
import pandas as pd
from pathlib import Path


# ==========================================
# 1. LOCALIZAÇÃO DA PLANILHA
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

CAMINHO_MONITORAMENTO = (
    BASE_DIR / "data" / "Monitoramento da EP.xlsx"
)

ABA_EQUIPES = "Equipes"


# ==========================================
# 2. CARREGAMENTO DA BASE TERRITORIAL
# ==========================================

@st.cache_data
def carregar_base_territorial():

    if not CAMINHO_MONITORAMENTO.exists():
        raise FileNotFoundError(
            "A planilha Monitoramento da EP.xlsx não foi encontrada."
        )

    df = pd.read_excel(
        CAMINHO_MONITORAMENTO,
        sheet_name=ABA_EQUIPES,
        engine="openpyxl"
    )

    # Identificação das colunas pela posição
    # A = Distrito
    # B = CNES
    # C = USF
    # D = Equipe
    # E = INE

    if df.shape[1] < 5:
        raise ValueError(
            "A aba Equipes não possui todas as colunas esperadas."
        )

    base = pd.DataFrame({
        "Distrito": df.iloc[:, 0],
        "CNES": df.iloc[:, 1],
        "Unidade": df.iloc[:, 2],
        "Equipe": df.iloc[:, 3],
        "INE": df.iloc[:, 4]
    })

    # Limpeza dos campos de texto
    for coluna in ["CNES", "Unidade", "Equipe", "INE"]:
        base[coluna] = (
            base[coluna]
            .astype("string")
            .str.strip()
        )

    base["Distrito"] = pd.to_numeric(
        base["Distrito"],
        errors="coerce"
    )

    # Remover registros sem identificação territorial
    base = base.dropna(
        subset=["Distrito", "Unidade", "Equipe"]
    ).copy()

    base["Distrito"] = (
        base["Distrito"].astype(int)
    )

    # Remover duplicidades da relação territorial
    base = base.drop_duplicates(
        subset=["Distrito", "CNES", "Unidade", "Equipe", "INE"]
    )

    return base.reset_index(drop=True)


# ==========================================
# 3. LISTAR DISTRITOS
# ==========================================

def listar_distritos(base):

    return sorted(
        base["Distrito"].dropna().unique().tolist()
    )


# ==========================================
# 4. LISTAR UNIDADES POR DISTRITO
# ==========================================

def listar_unidades(base, distrito):

    dados = base.copy()

    if distrito != "Todos":

        dados = dados[
            dados["Distrito"] == distrito
        ]

    unidades = (
        dados[["CNES", "Unidade"]]
        .drop_duplicates()
        .sort_values("Unidade")
    )

    return unidades


# ==========================================
# 5. LISTAR EQUIPES POR UNIDADE
# ==========================================

def listar_equipes(base, distrito, unidade):

    dados = base.copy()

    if distrito != "Todos":

        dados = dados[
            dados["Distrito"] == distrito
        ]

    if unidade != "Todas":

        dados = dados[
            dados["Unidade"] == unidade
        ]

    equipes = (
        dados[["Equipe", "INE"]]
        .drop_duplicates()
        .sort_values("Equipe")
    )

    return equipes
