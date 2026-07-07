Rede Chromos Matcher - Sistema de Matching de Alunos

Sistema inteligente para identificar correspondências entre alunos aprovados em processos seletivos e a base de alunos da rede de cursos, utilizando técnicas avançadas de similaridade de nomes e validação de CPF.
📋 Índice

    Sobre o Projeto

    Tecnologias

    Como Funciona

    Instalação

    Uso

    Exemplos de Resultados

    Desafios e Soluções

    Estrutura do Código

    Melhorias Futuras

    IA no Desenvolvimento

📖 Sobre o Projeto

O Rede Chromos Matcher é uma aplicação desenvolvida para automatizar o processo de identificação de alunos que já possuem cadastro no sistema da rede de cursos. O sistema processa arquivos CSV com listas de alunos aprovados e alunos cadastrados, realizando matching inteligente através de múltiplas estratégias.
🎯 Objetivos

    Identificar alunos que já existem na base mesmo com variações de nome (acentos, maiúsculas/minúsculas, erros de digitação)

    Classificar a confiança do match em quatro níveis: ALTA, PROVÁVEL, BAIXA e SEM CORRESPONDÊNCIA

    Explicar o motivo da classificação através de observações detalhadas

    Processar grandes volumes de dados via arquivos CSV

🛠️ Tecnologias
Tecnologia	Versão	Finalidade
PHP	8.2.12	Linguagem principal
Laravel	12.62.0	Framework MVC
SQLite	-	Gerenciamento de sessões
HTML/CSS	-	Interface do usuário
CSV	-	Importação/Exportação de dados
🔍 Como Funciona
1. Normalização de Nomes

O problema: Nomes vêm de fontes diferentes com formatações variadas.
text

"Letícia" ≠ "LETICIA"  (acentuação diferente)
"José"    ≠ "JOSE"     (maiúsculas/minúsculas)
"Vinícius" ≠ "VINICIUS" (ambos)

A solução: Normalização universal.
php

"Letícia"   → "LETICIA"  (remove acentos + maiúsculo)
"José"      → "JOSE"
"Vinícius"  → "VINICIUS"

2. Estratégias de Matching

O sistema utiliza 5 estratégias em cascata, da mais restritiva para a mais flexível:
text

┌─────────────────────────────────────────────────────┐
│              1. CPF EXATO                           │
│              ↓                                      │
│              2. NOME EXATO                         │
│              ↓                                      │
│              3. BLOCOS DE NOME                     │
│              ↓                                      │
│              4. SIMILARIDADE                       │
│              ↓                                      │
│              5. BUSCA FLEXÍVEL                     │
└─────────────────────────────────────────────────────┘

Estratégia 1: CPF Exato (Prioridade Máxima)
php

if ($cpf && isset($this->alunosPorCpf[$cpf])) {
    return 'EXATA (CPF)'; // Confiança: 100%
}

Estratégia 2: Nome Exato
php

$nomeNormalizado = NormalizadorNomes::normalizar($nome);
if (isset($this->alunosPorNomeNormalizado[$nomeNormalizado])) {
    return 'ALTA (nome)'; // Confiança: 100%
}

Estratégia 3: Blocos de Nome

Para "JOSE ANTONIO CARVALHO", o sistema gera múltiplos blocos:
php

$blocos = [
    "JCAR",      // J + CAR
    "JOCA",      // JO + CA
    "JOSCAR",    // JOS + CAR
    "JOSE",      // Primeiro nome
    "JOSANT",    // JOS + ANT
    "JOSEC"      // JOSE + C
];

Estratégia 4: Similaridade

Algoritmo híbrido: 60% Jaccard + 40% Levenshtein
php

// Exemplo: "Guilerme" vs "Guilherme"
// Jaccard: 0.85 (tokens comuns)
// Levenshtein: 0.90 (distância pequena)
// Score Final: 0.6 * 0.85 + 0.4 * 0.90 = 0.87

Estratégia 5: Busca Flexível
php

// Último recurso: busca pelo primeiro nome
if ($primeiroNome === $primeiroNomeAluno) {
    // Pode ser um match, confiança baixa
}

3. Algoritmo de Similaridade

Como funciona o NomeComparator:
php

public static function similaridade(string $nome1, string $nome2): float
{
    // 1. Normaliza ambos
    $nome1 = NormalizadorNomes::normalizar($nome1); // "JOSE ANTONIO CARVALHO"
    $nome2 = NormalizadorNomes::normalizar($nome2); // "JOSE ANTONIO CARVALHO"
    
    // 2. Tokeniza (divide em palavras)
    $t1 = ["JOSE", "ANTONIO", "CARVALHO"];
    $t2 = ["JOSE", "ANTONIO", "CARVALHO"];
    
    // 3. Calcula Jaccard (interseção / união)
    // 3 tokens comuns / 3 tokens totais = 1.0
    
    // 4. Calcula Levenshtein (distância entre textos)
    // Textos idênticos → 1.0
    
    // 5. Score final: 60% * 1.0 + 40% * 1.0 = 1.0
    return 1.0;
}

4. Classificação de Confiança
Confiança	Score	Critério
ALTA	≥ 0.85	Primeiro nome igual + score alto
PROVÁVEL	≥ 0.70	Primeiro nome igual ou similar
BAIXA	≥ 0.55	Score razoável mas baixa confiança
SEM CORRESPONDÊNCIA	< 0.55	Primeiro nome diferente
📥 Instalação
Pré-requisitos

    PHP 8.0 ou superior

    Composer

    Servidor Web (Apache/Nginx) ou PHP Built-in Server

Passos
bash

# 1. Clone o repositório
git clone [url-do-repositorio]

# 2. Entre no diretório
cd rede-chromos-matcher

# 3. Instale as dependências
composer install

# 4. Configure o ambiente
cp .env.example .env

# 5. Gere a chave da aplicação
php artisan key:generate

# 6. Execute o servidor
php artisan serve

A aplicação estará disponível em: http://localhost:8000
💻 Uso
Interface

    Acesse http://localhost:8000/matching

    Faça upload do arquivo de Aprovados (CSV)

    Faça upload do arquivo de Alunos (CSV)

    Clique em "Processar Matching"

    Visualize o resumo e detalhamento dos resultados

Formato dos CSVs
Arquivo de Aprovados
csv

nome;cpf_cadastradp;instituicao;curso;modalidade
JOSE ANTONIO CARVALHO;***.456.789-**;UFMG;Medicina;Ampla Concorrência
Maria Eduarda Santos;***.567.890-**;UFMG;Direito;Ampla Concorrência

Arquivo de Alunos
csv

id_aluno;nome_completo;cpf;unidade;turma;ano_matricula
1001;José Antônio Carvalho;123.456.789-01;Barro Preto;ENEM Extensivo A;2025
1002;Maria Eduarda dos Santos;234.567.890-12;Contagem;ENEM Extensivo B;2025

Exemplo de Resultado
csv

Nome Aprovado;CPF Aprovado;Instituição;ID Aluno;Nome Aluno;Confiança;Score;Observação
Letícia Mendes Pereira;;UFJF;1015;Letícia Mendes Pereira;ALTA (nome);0.9226;COMPARAÇÃO: "Letícia" → "LETICIA" | "Letícia" → "LETICIA" | IGUAIS: SIM

📊 Exemplos de Resultados
Casos de Sucesso
Nome Aprovado	Nome Aluno	Confiança	Score	Motivo
JOSE ANTONIO CARVALHO	José Antônio Carvalho	ALTA	1.0	Mesma pessoa, normalização perfeita
Letícia Mendes	Letícia Mendes	ALTA	0.9226	Acentuação normalizada
VINICIUS ALVES	Vinícius Alves	ALTA	0.9483	Acentuação normalizada
Guilerme Rodrigues	Guilherme Rodrigues	PROVÁVEL	0.8200	Erro de digitação
Rafael Nunes	Rafael Augusto Nunes	PROVÁVEL	0.7583	Nome com sobrenome adicional
Casos de Não-Match
Nome Aprovado	Nome Aluno	Confiança	Motivo
Marcela Fagundes	Marina Fagundes	SEM CORRESPONDÊNCIA	Primeiro nome diferente (MARCELA ≠ MARINA)
Lucas Oliveira Souza	Lucas Gabriel Freitas Diniz	BAIXA	Sobrenomes diferentes
Juliana Campos	Júlia Campos	SEM CORRESPONDÊNCIA	Primeiro nome diferente (JULIANA ≠ JULIA)
🚧 Desafios e Soluções
1. 🔴 Acentuação e Case Sensitive

Problema: "José" não era reconhecido como "JOSE"

Solução: Criamos o NormalizadorNomes que remove acentos e converte para maiúsculo.
php

"José" → "JOSE"
"Letícia" → "LETICIA"
"Vinícius" → "VINICIUS"

Resultado: Acentuação deixou de ser um problema.
2. 🔴 Comparação de Primeiro Nome

Problema: "Leticia" e "Letícia" não eram reconhecidas como iguais.

Solução: Isolamos a lógica de extração e normalização do primeiro nome.
php

private function extrairPrimeiroNome(string $nomeCompleto): string
{
    $normalizado = NormalizadorNomes::normalizar($nomeCompleto);
    $tokens = explode(' ', $normalizado);
    return $tokens[0] ?? '';
}

Resultado: "LETICIA" = "LETICIA" → ALTA
3. 🔴 Erros de Digitação

Problema: "Guilerme" não era reconhecido como "Guilherme"

Solução: Implementamos distância de Levenshtein.
php

$distancia = levenshtein("GUILERME", "GUILHERME");
// Resultado: 2 (G U I L E R M E vs G U I L H E R M E)
// Distância <= 2 → considerado similar

Resultado: "GUILERME" ≈ "GUILHERME" → PROVÁVEL
4. 🔴 Falsos Positivos

Problema: "Marcela Fagundes" estava matcheando com "Marina Fagundes"

Solução: Forçamos a verificação do primeiro nome.
php

if (!$primeiroNomeIgual) {
    // Rebaixa a confiança
    return 'BAIXA (nome)';
}

Resultado: "MARCELA" ≠ "MARINA" → SEM CORRESPONDÊNCIA
5. 🔴 Método Indefinido (Normalizer::nome)

Problema: Chamada de método inexistente.

Solução: Criamos o NormalizadorNomes com os métodos necessários.

Resultado: Normalização centralizada e consistente.
6. 🔴 Debug da Comparação

Problema: Difícil entender por que a comparação falhava.

Solução: Adicionamos debug detalhado na observação.
php

$debug = sprintf(
    'COMPARAÇÃO: "%s" → "%s" | "%s" → "%s" | IGUAIS: %s',
    $primeiroAprovadoOriginal,
    $primeiroAprovadoNormalizado,
    $primeiroAlunoOriginal,
    $primeiroAlunoNormalizado,
    $primeiroNomeIgual ? 'SIM' : 'NÃO'
);

Resultado: Visualização clara do processo de comparação.
7. 🔴 Blocos Restritivos

Problema: "JOSE ANTONIO CARVALHO" não encontrava "José Antônio Carvalho"

Solução: Geramos múltiplos blocos.
php

$blocos = [
    "JCAR", "JOCA", "JOSCAR", "JOSE", "JOSANT", "JOSEC"
];

Resultado: Match encontrado com sucesso.
🏗️ Estrutura do Código
NormalizadorNomes.php

Responsabilidade: Normalizar nomes (acentos, maiúsculas, espaços)
php

class NormalizadorNomes
{
    // Remove acentos e converte para MAIÚSCULO
    public static function normalizar(string $texto): string;
    
    // Extrai apenas o primeiro nome normalizado
    public static function primeiroNome(string $nome): string;
    
    // Extrai os sobrenomes normalizados
    public static function sobrenomes(string $nome): array;
    
    // Verifica se dois nomes são iguais (normalizados)
    public static function iguais(string $nome1, string $nome2): bool;
}

NomeComparator.php

Responsabilidade: Calcular similaridade entre nomes
php

class NomeComparator
{
    // Algoritmo híbrido: 60% Jaccard + 40% Levenshtein
    public static function similaridade(string $nome1, string $nome2): float;
    
    // Tokeniza e remove partículas (de, da, do, etc.)
    private static function tokenizar(string $nome): array;
}

MatcherService.php

Responsabilidade: Orquestrar o processo de matching
php

class MatcherService
{
    // Ponto de entrada: processa arrays de aprovados e alunos
    public function match(array $aprovados, array $alunos): array;
    
    // Retorna o resumo das confianças
    public function getResumo(): array;
    
    // Carrega e indexa os alunos (CPF, nome, blocos)
    private function carregarAlunos(array $alunos): void;
    
    // Processa um aprovado individualmente
    private function processarAprovado(array $aprovado): array;
    
    // Gera múltiplos blocos para busca
    private function gerarBlocos(string $nome): array;
}

Fluxo de Dados
text

┌─────────────────────────────────────────────────────────────┐
│                       FLUXO DE DADOS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CSV Aprovados ───→ MatcherService::match()                │
│         ↓                                                   │
│  CSV Alunos ──────→ MatcherService::carregarAlunos()       │
│         ↓                                                   │
│         ├── Indexa por CPF                                  │
│         ├── Indexa por Nome Normalizado                    │
│         └── Indexa por Blocos                              │
│         ↓                                                   │
│  Para cada aprovado:                                       │
│         ├── Tenta CPF Exato                                │
│         ├── Tenta Nome Exato                               │
│         ├── Tenta Blocos                                   │
│         ├── Tenta Similaridade                             │
│         └── Tenta Busca Flexível                          │
│         ↓                                                   │
│  Resultado:                                                │
│         ├── Nome Aprovado                                  │
│         ├── Nome Aluno                                     │
│         ├── Confiança                                      │
│         ├── Score                                          │
│         └── Observação                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘

🚀 Melhorias Futuras
Curto Prazo

    Suporte a abreviações (ex: "Ant." → "Antonio")

    Exportação de resultados em Excel

    Interface para revisão manual de casos ambíguos

    Validação de CPF completo (dígitos verificadores)

Médio Prazo

    Peso por instituição/curso para melhorar o matching

    Histórico de matches para aprendizado

    API REST para integração com outros sistemas

    Suporte a múltiplos formatos de arquivo (XLSX, JSON)

Longo Prazo

    Machine Learning para melhorar a classificação

    Sistema de feedback para refinar o algoritmo

    Dashboard com métricas e KPIs

    Matching automático em tempo real

🤖 IA no Desenvolvimento
Como a IA foi utilizada
Etapa	Contribuição da IA
Geração Inicial	Estruturação da lógica de matching
Normalização	Criação do NormalizadorNomes para centralizar a lógica
Correção de Bugs	Identificação e correção de problemas como Normalizer::nome() inexistente
Otimização	Melhorias no cálculo de similaridade (Jaccard + Levenshtein)
Debug	Implementação do sistema de debug com observações detalhadas
Blocos	Sugestão de múltiplos blocos para aumentar chances de match
Prompts Utilizados
    "Isole a normalização em uma classe separada"
    "Adicione distância de Levenshtein para nomes similares"

Aprendizados com a IA

    Normalização é fundamental: Sem normalização, a comparação falha

    Múltiplas estratégias: Nenhuma única abordagem funciona para todos os casos

    Debug visual: Mostrar o processo ajuda a identificar problemas

    Separação de responsabilidades: Código organizado é mais fácil de manter

    Testes com dados reais: Sempre valide com exemplos reais
