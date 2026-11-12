
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import streamlit.components.v1 as components
import html
import math
from modules.conexao_google import carregar_atividades_atuais

from config import (
    NOME_PLANILHA,
    ABA_PLANILHA,
    ATIVIDADES,
    COLUNA_DS,
    COR_SIM,
    COR_NAO,
    COR_NAO_SE_APLICA
)

# ==========================================
# 1. LOCALIZAÇÃO DA PLANILHA
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

CAMINHO_PLANILHA = BASE_DIR / "data" / NOME_PLANILHA


# ==========================================
# 2. CONVERSÃO DE LETRAS EM COLUNAS
# ==========================================

def letra_para_indice(letra):
    """Converte a letra Excel em índice numérico."""
    resultado = 0

    for caractere in letra.upper():
        resultado = resultado * 26 + ord(caractere) - 64

    return resultado - 1


# ==========================================
# 3. CARREGAMENTO DA PLANILHA
# ==========================================

@st.cache_data(ttl=60)
def carregar_dados():

    try:
        dados = carregar_atividades_atuais()

        if not dados:
            return None

        df = pd.DataFrame(dados)

        return df

    except Exception as erro:
        st.error(f"Erro ao carregar dados do Google Sheets: {erro}")
        return None


# ==========================================
# 4. PREPARAÇÃO DOS DADOS
# ==========================================

def preparar_indicador(df, nome_atividade, configuracao):

    indice_status = letra_para_indice(
        configuracao["status"]
    )

    indice_data = letra_para_indice(
        configuracao["data"]
    )

    indice_ds = letra_para_indice(COLUNA_DS)

    dados = pd.DataFrame({
        "DS": df.iloc[:, indice_ds],
        "Status": df.iloc[:, indice_status],
        "Data prevista": df.iloc[:, indice_data]
    })

    # Remover linhas sem identificação do DS
    dados = dados.dropna(subset=["DS"]).copy()

    # Padronizar respostas
    dados["Status"] = (
        dados["Status"]
        .astype("string")
        .str.strip()
        .str.casefold()
        .map({
            "sim": "Sim",
            "não": "Não",
            "nao": "Não",
            "não se aplica": "Não se aplica",
            "nao se aplica": "Não se aplica"
        })
    )

    # Converter datas
    dados["Data prevista"] = pd.to_datetime(
        dados["Data prevista"],
        errors="coerce",
        dayfirst=True
    )

    return dados


# ==========================================
# 5. CONTAGEM DAS RESPOSTAS
# ==========================================

def calcular_indicadores(dados):

    contagem = (
        dados["Status"]
        .value_counts()
        .reindex(
            ["Sim", "Não", "Não se aplica"],
            fill_value=0
        )
    )

    total = int(contagem.sum())

    realizados = int(contagem["Sim"])
    pendentes = int(contagem["Não"])
    nao_aplica = int(contagem["Não se aplica"])

    percentual = (
        realizados / total * 100
        if total > 0 else 0
    )

    return {
        "total": total,
        "sim": realizados,
        "nao": pendentes,
        "nao_se_aplica": nao_aplica,
        "percentual": percentual
    }


# ==========================================
# 6. GRÁFICO DE ROSCA COM HOVER
# ==========================================

def criar_grafico(dados, nome_atividade):

    contagem = calcular_indicadores(dados)

    grafico = pd.DataFrame({
        "Situação": ["Sim", "Não", "Não se aplica"],
        "Quantidade": [
            contagem["sim"],
            contagem["nao"],
            contagem["nao_se_aplica"]
        ]
    })

    # Não exibir categorias sem registros
    grafico = grafico[grafico["Quantidade"] > 0]

    cores = {
        "Sim": COR_SIM,
        "Não": COR_NAO,
        "Não se aplica": COR_NAO_SE_APLICA
    }

    fig = px.pie(
        grafico,
        names="Situação",
        values="Quantidade",
        hole=0.62,
        color="Situação",
        color_discrete_map=cores,
        custom_data=["Quantidade"]
    )

    fig.update_traces(
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Quantidade: %{value}<br>"
            "Percentual: %{percent}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        title=nome_atividade,
        showlegend=True,
        margin=dict(t=55, b=15, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.12)
    )

    return fig


# ==========================================
# 7. TABELA DE PENDÊNCIAS
# ==========================================

def obter_faltantes(dados):

    faltantes = dados[
        dados["Status"] == "Não"
    ].copy()

    faltantes["Data prevista"] = (
        faltantes["Data prevista"]
        .dt.strftime("%d/%m/%Y")
        .fillna("Data não informada")
    )

    return faltantes[
        ["DS", "Status", "Data prevista"]
    ]


# ==========================================
# 8. EXIBIÇÃO DE CADA ATIVIDADE
# ==========================================

def exibir_atividade(nome, configuracao, df):

    dados = preparar_indicador(
        df,
        nome,
        configuracao
    )

    indicadores = calcular_indicadores(dados)

    st.markdown(f"### {nome}")

    col_grafico, col_tabela = st.columns([1, 1.5])

    with col_grafico:

        st.plotly_chart(
            criar_grafico(dados, nome),
            use_container_width=True,
            key=f"grafico_{configuracao['status']}"
        )

        st.metric(
            "Percentual de realização",
            f"{indicadores['percentual']:.1f}%"
        )

    with col_tabela:

        st.markdown("#### Treinamentos pendentes")

        faltantes = obter_faltantes(dados)

        if faltantes.empty:
            st.success("Não existem atividades pendentes.")
        else:
            st.dataframe(
                faltantes,
                hide_index=True,
                use_container_width=True
            )

    st.caption(
        f"Total: {indicadores['total']} | "
        f"Sim: {indicadores['sim']} | "
        f"Não: {indicadores['nao']} | "
        f"Não se aplica: {indicadores['nao_se_aplica']}"
    )

    st.divider()


# ==========================================
# 9. CARD INTERATIVO COM TABELA NO HOVER
# ==========================================

def criar_card_hover(nome, dados):

    indicadores = calcular_indicadores(dados)

    categorias = [
        ("Sim", indicadores["sim"], COR_SIM),
        ("Não", indicadores["nao"], COR_NAO),
        ("Não se aplica", indicadores["nao_se_aplica"], COR_NAO_SE_APLICA)
    ]

    total = indicadores["total"]
    raio = 65
    circunferencia = 2 * math.pi * raio
    deslocamento = 0

    segmentos = []

    for rotulo, quantidade, cor in categorias:

        if quantidade == 0 or total == 0:
            continue

        comprimento = (quantidade / total) * circunferencia

        segmentos.append(
            f"""
            <circle
                cx="90" cy="90" r="{raio}"
                fill="none"
                stroke="{cor}"
                stroke-width="23"
                stroke-dasharray="{comprimento} {circunferencia - comprimento}"
                stroke-dashoffset="-{deslocamento}"
            />
            """
        )

        deslocamento += comprimento

    svg = f"""
    <svg viewBox="0 0 180 180" width="175" height="175">
        <g transform="rotate(-90 90 90)">
            {''.join(segmentos)}
        </g>
        <text x="90" y="86" text-anchor="middle"
              font-size="25" font-weight="bold" fill="#173568">
            {total}
        </text>
        <text x="90" y="108" text-anchor="middle"
              font-size="12" fill="#666">
            Registros
        </text>
    </svg>
    """

    legenda = "".join(
        f"""
        <span class="legenda-item">
            <span class="bolinha" style="background:{cor}"></span>
            {rotulo}: {quantidade}
        </span>
        """
        for rotulo, quantidade, cor in categorias
    )

    linhas = []

    for _, registro in dados.iterrows():

        ds = html.escape(str(registro["DS"]))
        status = html.escape(str(registro["Status"]))

        data = registro["Data prevista"]

        if pd.isna(data):
            data_texto = "Data não informada"
        else:
            data_texto = data.strftime("%d/%m/%Y")

        data_texto = html.escape(data_texto)

        linhas.append(
            f"""
            <tr>
                <td>{ds}</td>
                <td>{status}</td>
                <td>{data_texto}</td>
            </tr>
            """
        )

    titulo = html.escape(nome)

    percentual = indicadores["percentual"]

    conteudo = f"""
    <html>
    <head>
    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: transparent;
        }}

        .card {{
            position: relative;
            height: 305px;
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            overflow: visible;
        }}

        .titulo {{
            font-size: 15px;
            font-weight: bold;
            color: #173568;
            min-height: 38px;
            line-height: 19px;
        }}

        .grafico {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 185px;
        }}

        .legenda {{
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            font-size: 11px;
            color: #444;
        }}

        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .bolinha {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
        }}

        .percentual {{
            text-align: center;
            font-size: 12px;
            color: #173568;
            font-weight: bold;
            margin-top: 5px;
        }}

        .janela {{
            display: none;
            position: absolute;
            z-index: 9999;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #FFFFFF;
            border: 2px solid #173568;
            border-radius: 14px;
            padding: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.20);
        }}

        .card:hover .janela {{
            display: block;
        }}

        .janela h4 {{
            margin: 0 0 10px 0;
            color: #173568;
            font-size: 14px;
        }}

        .tabela-container {{
            max-height: 235px;
            overflow-y: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}

        th {{
            background: #173568;
            color: white;
            position: sticky;
            top: 0;
        }}

        th, td {{
            padding: 7px 5px;
            border: 1px solid #E5E7EB;
            text-align: left;
        }}

        tr:nth-child(even) {{
            background: #F3F4F7;
        }}

        .instrucao {{
            font-size: 10px;
            color: #777;
            text-align: center;
            margin-top: 5px;
        }}

    </style>
    </head>

    <body>

        <div class="card">

            <div class="titulo">{titulo}</div>

            <div class="grafico">
                {svg}
            </div>

            <div class="legenda">
                {legenda}
            </div>

            <div class="percentual">
                Realização: {percentual:.1f}%
            </div>

            <div class="instrucao">
                Passe o mouse para consultar os registros
            </div>

            <div class="janela">

                <h4>{titulo} — Registros</h4>

                <div class="tabela-container">

                    <table>
                        <thead>
                            <tr>
                                <th>DS</th>
                                <th>Status</th>
                                <th>Data prevista</th>
                            </tr>
                        </thead>

                        <tbody>
                            {''.join(linhas)}
                        </tbody>
                    </table>

                </div>

            </div>

        </div>

    </body>
    </html>
    """

    components.html(
        conteudo,
        height=320,
        scrolling=False
    )



# ==========================================
# 10. GRADE DOS OITO INDICADORES
# ==========================================

def exibir_grade_atividades(df):

    atividades = list(ATIVIDADES.items())

    # Organizar os cards em três colunas
    quantidade_colunas = 3

    for inicio in range(0, len(atividades), quantidade_colunas):

        grupo = atividades[inicio:inicio + quantidade_colunas]

        colunas = st.columns(quantidade_colunas, gap="medium")

        for coluna, (nome, configuracao) in zip(colunas, grupo):

            # Preparar os dados de cada atividade
            dados = preparar_indicador(
                df,
                nome,
                configuracao
            )

            # Exibir o card interativo
            with coluna:

                criar_card_hover(
                    nome,
                    dados
                )

