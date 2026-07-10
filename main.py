import pandas as pd
import re
from difflib import SequenceMatcher


def normalizar_nome(nome):
    """Normaliza nomes para comparação"""
    if pd.isna(nome) or nome == '':
        return ""
    # Remove acentos e caracteres especiais
    nome = str(nome).upper()
    # Remove pontuação
    nome = re.sub(r'[^\w\s]', '', nome)
    # Remove múltiplos espaços
    nome = re.sub(r'\s+', ' ', nome).strip()
    return nome


def extrair_sobrenomes(nome):
    """Extrai lista de sobrenomes para comparação"""
    partes = nome.split()
    if len(partes) > 1:
        return set(partes[1:])  # Todos exceto o primeiro nome
    return set()


def grau_confianca(nome_aprovado, nome_base, cpf_aprovado, cpf_base):
    """
    Calcula grau de confiança baseado em nome e CPF
    Retorna: 'Alto', 'Médio', 'Baixo' ou 'Nulo'
    """
    # Se CPF corresponde exatamente (considerando apenas os 9 primeiros dígitos)
    if cpf_aprovado and cpf_base and not pd.isna(cpf_aprovado) and not pd.isna(cpf_base):
        # Extrai apenas números do CPF
        nums_aprovado = re.sub(r'\D', '', str(cpf_aprovado))
        nums_base = re.sub(r'\D', '', str(cpf_base))

        # Verifica se os 9 primeiros dígitos correspondem (CPF mascarado)
        if len(nums_aprovado) >= 9 and len(nums_base) >= 9:
            if nums_aprovado[:9] == nums_base[:9]:
                return "Alto"

    # Se não tem CPF, compara nome
    if nome_aprovado and nome_base:
        nome_aprovado_norm = normalizar_nome(nome_aprovado)
        nome_base_norm = normalizar_nome(nome_base)

        # Similaridade do nome completo
        similaridade = SequenceMatcher(None, nome_aprovado_norm, nome_base_norm).ratio()

        if similaridade >= 0.9:
            return "Alto"
        elif similaridade >= 0.7:
            # Verifica sobrenomes
            sobrenomes_aprovado = extrair_sobrenomes(nome_aprovado_norm)
            sobrenomes_base = extrair_sobrenomes(nome_base_norm)

            if len(sobrenomes_aprovado) > 0 and len(sobrenomes_base) > 0:
                interseccao = sobrenomes_aprovado & sobrenomes_base
                if len(interseccao) >= min(len(sobrenomes_aprovado), len(sobrenomes_base)) * 0.5:
                    return "Médio"

            # Verifica primeiro nome
            primeiro_aprovado = nome_aprovado_norm.split()[0] if nome_aprovado_norm else ""
            primeiro_base = nome_base_norm.split()[0] if nome_base_norm else ""

            if primeiro_aprovado == primeiro_base:
                return "Médio"

            return "Médio"

        elif similaridade >= 0.5:
            return "Baixo"

    return "Nulo"


def encontrar_melhor_match(aprovado, base_alunos):
    """
    Encontra o melhor match para um aprovado na base de alunos
    """
    melhor_match = None
    melhor_confianca = "Nulo"
    melhor_score = -1

    cpf_aprovado = aprovado.get('cpf_mascarado', '')
    nome_aprovado = aprovado['nome']

    for _, aluno in base_alunos.iterrows():
        confianca = grau_confianca(
            nome_aprovado,
            aluno['nome_completo'],
            cpf_aprovado,
            aluno['cpf']
        )

        # Calcula score para ordenação
        score_map = {"Alto": 3, "Médio": 2, "Baixo": 1, "Nulo": 0}
        score = score_map.get(confianca, 0)

        if score > melhor_score:
            melhor_score = score
            melhor_confianca = confianca
            melhor_match = aluno
        elif score == melhor_score and melhor_match is not None and confianca != "Nulo":
            # Em caso de empate, verifica similaridade de nome
            similaridade = SequenceMatcher(
                None,
                normalizar_nome(nome_aprovado),
                normalizar_nome(aluno['nome_completo'])
            ).ratio()

            similaridade_atual = SequenceMatcher(
                None,
                normalizar_nome(nome_aprovado),
                normalizar_nome(melhor_match['nome_completo'])
            ).ratio()

            if similaridade > similaridade_atual:
                melhor_match = aluno
                melhor_confianca = confianca

    return melhor_match, melhor_confianca


def gerar_relatorio(arquivo_aprovados, arquivo_base):
    """
    Gera relatório completo de correspondência
    """
    # Carregar dados
    aprovados = pd.read_csv(arquivo_aprovados, sep=';', encoding='utf-8')
    base_alunos = pd.read_csv(arquivo_base, sep=';', encoding='utf-8')

    # Limpar dados
    aprovados['nome'] = aprovados['nome'].fillna('').str.strip()
    aprovados['cpf_mascarado'] = aprovados['cpf_mascarado'].fillna('')
    base_alunos['nome_completo'] = base_alunos['nome_completo'].fillna('').str.strip()
    base_alunos['cpf'] = base_alunos['cpf'].fillna('')

    resultados = []
    estatisticas = {'Alto': 0, 'Médio': 0, 'Baixo': 0, 'Nulo': 0}

    for _, aprovado in aprovados.iterrows():
        match, confianca = encontrar_melhor_match(aprovado, base_alunos)

        resultado = {
            'Aprovado': aprovado['nome'],
            'CPF_Mascarado': aprovado['cpf_mascarado'],
            'Instituicao': aprovado['instituicao'],
            'Curso': aprovado['curso'],
            'Modalidade': aprovado['modalidade'],
            'Corresponde': 'Sim' if match is not None else 'Não',
            'ID_Aluno': match['id_aluno'] if match is not None else '-',
            'Nome_Base': match['nome_completo'] if match is not None else '-',
            'Unidade': match['unidade'] if match is not None else '-',
            'Turma': match['turma'] if match is not None else '-',
            'Ano_Matricula': match['ano_matricula'] if match is not None else '-',
            'Grau_Confianca': confianca
        }

        resultados.append(resultado)
        estatisticas[confianca] = estatisticas.get(confianca, 0) + 1

    # Criar DataFrame de resultados
    df_resultados = pd.DataFrame(resultados)

    # Gerar resumo
    resumo = {
        'Total_Aprovados': len(aprovados),
        'Total_Encontrados': len([r for r in resultados if r['Corresponde'] == 'Sim']),
        'Total_Nao_Encontrados': len([r for r in resultados if r['Corresponde'] == 'Não']),
        'Alto_Confianca': estatisticas['Alto'],
        'Medio_Confianca': estatisticas['Médio'],
        'Baixo_Confianca': estatisticas['Baixo'],
        'Nulo_Confianca': estatisticas['Nulo']
    }

    return df_resultados, resumo


def imprimir_relatorio(df_resultados, resumo):
    """
    Imprime o relatório no console
    """
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO DE CORRESPONDÊNCIA ENTRE APROVADOS E ALUNOS DA REDE")
    print("=" * 80)

    print("\n📋 LISTA DE CORRESPONDÊNCIAS:")
    print("-" * 120)

    # Formatação para exibição
    for _, row in df_resultados.iterrows():
        print(f"\nAprovado: {row['Aprovado']}")
        print(f"  CPF: {row['CPF_Mascarado']}")
        print(f"  Instituição: {row['Instituicao']} - {row['Curso']}")
        print(f"  Corresponde? {'✅ Sim' if row['Corresponde'] == 'Sim' else '❌ Não'}")
        if row['Corresponde'] == 'Sim':
            print(f"  → ID: {row['ID_Aluno']} | Nome: {row['Nome_Base']}")
            print(f"  → Unidade: {row['Unidade']} | Turma: {row['Turma']} | Ano: {row['Ano_Matricula']}")
            print(f"  → Grau de Confiança: {row['Grau_Confianca']}")
        else:
            print(f"  → {row['Grau_Confianca']} (não encontrado)")

    print("\n" + "=" * 80)
    print("📈 RESUMO ESTATÍSTICO")
    print("=" * 80)
    print(f"Total de Aprovados: {resumo['Total_Aprovados']}")
    print(f"Total de Correspondências Encontradas: {resumo['Total_Encontrados']}")
    print(f"Total de Não Encontrados: {resumo['Total_Nao_Encontrados']}")
    print("\nGrau de Confiança:")
    print(f"  🟢 Alto: {resumo['Alto_Confianca']}")
    print(f"  🟡 Médio: {resumo['Medio_Confianca']}")
    print(f"  🟠 Baixo: {resumo['Baixo_Confianca']}")
    print(f"  ⚪ Nulo (não encontrado): {resumo['Nulo_Confianca']}")
    print("=" * 80)


def salvar_resultados(df_resultados, resumo):
    """
    Salva os resultados em arquivos CSV
    """
    # Salvar lista de correspondências
    df_resultados.to_csv('relatorio_correspondencias.csv', sep=';', index=False, encoding='utf-8-sig')
    print("✅ Relatório de correspondências salvo como: relatorio_correspondencias.csv")

    # Salvar resumo
    df_resumo = pd.DataFrame([resumo])
    df_resumo.to_csv('resumo_estatistico.csv', sep=';', index=False, encoding='utf-8-sig')
    print("✅ Resumo estatístico salvo como: resumo_estatistico.csv")


# ============ EXECUÇÃO PRINCIPAL ============
if __name__ == "__main__":
    # Nomes dos arquivos
    ARQUIVO_APROVADOS = "aprovados instituicoes.csv"
    ARQUIVO_BASE = "base alunos.csv"

    try:
        print("🔄 Processando dados...")

        # Gerar relatório
        df_resultados, resumo = gerar_relatorio(ARQUIVO_APROVADOS, ARQUIVO_BASE)

        # Imprimir no console
        imprimir_relatorio(df_resultados, resumo)

        # Salvar em CSV
        salvar_resultados(df_resultados, resumo)

        # Exibir os primeiros registros do resumo
        print("\n📊 Amostra do relatório gerado:")
        print(df_resultados[['Aprovado', 'Corresponde', 'ID_Aluno', 'Grau_Confianca']].head(10).to_string(index=False))

    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo não encontrado - {e}")
        print("   Verifique se os arquivos estão na mesma pasta do script")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback

        traceback.print_exc()