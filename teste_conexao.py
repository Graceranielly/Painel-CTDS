
from modules.conexao_google import carregar_atividades_atuais

try:
    dados = carregar_atividades_atuais()

    print("\nCONEXÃO REALIZADA COM SUCESSO!")
    print(f"Quantidade de registros: {len(dados)}")

    if dados:
        print("\nColunas encontradas:")
        print(list(dados[0].keys()))

        print("\nPrimeiro registro:")
        print(dados[0])

except Exception as erro:
    print("\nERRO NA CONEXÃO:")
    print(erro)
    
    
from modules.conexao_google import obter_ultima_atualizacao

print("\nÚLTIMA ATUALIZAÇÃO DA PLANILHA:")
print(obter_ultima_atualizacao())