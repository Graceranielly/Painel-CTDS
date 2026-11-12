
# ==================================================
# CONFIGURAÇÕES DO SISTEMA
# SALA DE SITUAÇÃO - EDUCAÇÃO PERMANENTE
# ==================================================

# 1. IDENTIFICAÇÃO DO SISTEMA

NOME_SISTEMA = "Sala de Situação"

NOME_MODULO = "Educação Permanente"


# 2. ARQUIVO E ABA DA PLANILHA

NOME_PLANILHA = "Sala de Situação.xlsx"

ABA_PLANILHA = "Atividades Atuais"


# 3. IDENTIDADE VISUAL

COR_PRIMARIA = "#173568"

COR_SECUNDARIA = "#F3F4F7"

COR_SIM = "#16A34A"

COR_NAO = "#E33448"

COR_NAO_SE_APLICA = "#172BB5"

COR_TEXTO = "#202124"

COR_BRANCO = "#FFFFFF"


# 4. IDENTIFICAÇÃO DOS REGISTROS

COLUNA_DS = "A"



# 5. MAPEAMENTO DAS ATIVIDADES E DATAS

ATIVIDADES = {

    "Treinamento dos Conselhos Distritais em Saúde": {
        "status": "G",
        "data": "H"
    },

    "Treinamento dos Compaz": {
        "status": "I",
        "data": "J"
    },

    "Treinamento dos Faltosos 1 - 2026.2": {
        "status": "K",
        "data": "L"
    },

    "Colegiado dos Gerentes de Unidades 2026.2": {
        "status": "O",
        "data": "P"
    },

    "Educação Permanente com EMULTI": {
        "status": "S",
        "data": "T"
    },

    "Educação Permanente com PAC": {
        "status": "U",
        "data": "V"
    }

}

# As duas atividades restantes serão adicionadas
# após a confirmação dos cabeçalhos da planilha.



# 6. STATUS DAS ATIVIDADES

STATUS_SIM = "Sim"

STATUS_NAO = "Não"

STATUS_NAO_SE_APLICA = "Não se aplica"
