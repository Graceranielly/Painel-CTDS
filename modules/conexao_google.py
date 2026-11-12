
from pathlib import Path
import json
import gspread

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build



# Caminhos dos arquivos
PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_CREDENCIAIS = PASTA_PROJETO / "credentials.json"
ARQUIVO_TOKEN = PASTA_PROJETO / "token.json"

# Permissões somente de leitura: Google Sheets e metadados do Drive
ESCOPO = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly"
]

# ID da planilha Sala de Situação
ID_PLANILHA = "1LFEWi4AJVdn4g_7TcyOfn7Hnq-ISi6W-e3-_Pp4DrWs"

# Aba que será consultada
NOME_ABA = "Atividades Atuais"


def conectar_google():
    credenciais = None

    if ARQUIVO_TOKEN.exists():
        credenciais = Credentials.from_authorized_user_file(
            str(ARQUIVO_TOKEN), ESCOPO
        )

    if credenciais and credenciais.expired and credenciais.refresh_token:
        credenciais.refresh(Request())

    if not credenciais or not credenciais.valid:
        fluxo = InstalledAppFlow.from_client_secrets_file(
            str(ARQUIVO_CREDENCIAIS),
            ESCOPO
        )

        credenciais = fluxo.run_local_server(port=0)

        ARQUIVO_TOKEN.write_text(
            credenciais.to_json(),
            encoding="utf-8"
        )

    cliente = gspread.authorize(credenciais)

    return cliente

def obter_credenciais_google():
    credenciais = None

    if ARQUIVO_TOKEN.exists():
        credenciais = Credentials.from_authorized_user_file(
            str(ARQUIVO_TOKEN), ESCOPO
        )

    if credenciais and credenciais.expired and credenciais.refresh_token:
        credenciais.refresh(Request())

        ARQUIVO_TOKEN.write_text(
            credenciais.to_json(),
            encoding="utf-8"
        )

    if not credenciais or not credenciais.valid:
        fluxo = InstalledAppFlow.from_client_secrets_file(
            str(ARQUIVO_CREDENCIAIS),
            ESCOPO
        )

        credenciais = fluxo.run_local_server(port=0)

        ARQUIVO_TOKEN.write_text(
            credenciais.to_json(),
            encoding="utf-8"
        )

    return credenciais



def carregar_atividades_atuais():
    cliente = conectar_google()

    planilha = cliente.open_by_key(ID_PLANILHA)

    aba = planilha.worksheet(NOME_ABA)

    valores = aba.get_all_values()

    if not valores:
        return []
    
    

    cabecalhos = valores[0]

    # Corrigir automaticamente títulos repetidos
    contagem = {}
    cabecalhos_unicos = []

    for nome in cabecalhos:
        nome = nome.strip() or "Coluna"

        contagem[nome] = contagem.get(nome, 0) + 1

        if contagem[nome] > 1:
            nome = f"{nome}_{contagem[nome]}"

        cabecalhos_unicos.append(nome)

    dados = []

    for linha in valores[1:]:
        linha = linha + [""] * (len(cabecalhos_unicos) - len(linha))

        registro = dict(zip(cabecalhos_unicos, linha))

        dados.append(registro)

    return dados


def obter_ultima_atualizacao():
    credenciais = obter_credenciais_google()

    servico_drive = build(
        "drive",
        "v3",
        credentials=credenciais
    )

    arquivo = servico_drive.files().get(
        fileId=ID_PLANILHA,
        fields="name,modifiedTime",
        supportsAllDrives=True
    ).execute()

    return arquivo.get("modifiedTime")

