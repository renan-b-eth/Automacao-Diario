# 🎯 Bot de Rastreamento de Concursos ETEC/FATEC

Crawler autônomo em Python que monitora **todas** as páginas de processos seletivos e concursos públicos do CPS (URH) — ETEC e FATEC — e o **Diário Oficial do Estado de SP (DOE SP)** em busca do seu nome. Envia notificações detalhadas via WhatsApp (CallMeBot) com edital, unidade, cidade, disciplina e fase do processo.

## Como funciona

### Fase 1 — Portal CPS (URH)

1. **Descoberta automática:** Acessa as 11 páginas de listagem do portal CPS (Inscrições Abertas + Em Andamento) para ETEC, FATEC e PSSAD
2. **Extração de processos:** Identifica todos os links de detalhes de processos seletivos em cada listagem
3. **Metadados:** Extrai nº do edital, unidade de ensino (ETEC/FATEC), cidade e disciplina
4. **Classificação de fase:** Identifica automaticamente a fase do documento (Abertura → Deferimento → Classificação → Convocação…)
5. **Varredura profunda:** Para cada processo, coleta os links de documentos (PDF e DOCX) — editais, classificações, convocações, etc.
6. **Análise de texto:** Baixa documentos novos **na memória** e busca pelo seu nome (case insensitive)

### Fase 2 — Diário Oficial do Estado de SP (DOE SP)

7. **Busca via API:** Consulta a API pública do DOE SP buscando seu nome no caderno Executivo (últimos 30 dias)
8. **Publicações oficiais:** Detecta nomeações, convocações, homologações e qualquer citação do seu nome no Diário Oficial

### Notificações

- 🚨 **Nome encontrado no CPS** → alerta com edital, unidade, cidade, disciplina e fase
- ⚠️ **Documento novo sem nome** → alerta de nova movimentação no processo
- 📰 **Nome no DOE SP** → alerta com título, data, seção e trecho da publicação
- **Cache inteligente:** `history_pdfs.json` evita notificações repetidas

### Fontes monitoradas

| Fonte | Categoria | Tipo | Páginas |
|---|---|---|---|
| CPS | ETEC | PSS (Processo Seletivo Simplificado) | Inscrições Abertas + Em Andamento |
| CPS | ETEC | CPD (Concurso Público Docente) | Inscrições Abertas + Em Andamento |
| CPS | ETEC | Auxiliar de Docente | Em Andamento |
| CPS | FATEC | PSS | Inscrições Abertas + Em Andamento |
| CPS | FATEC | CPD | Inscrições Abertas + Em Andamento |
| CPS | PSSAD | Auxiliar de Docente (ETEC/FATEC) | Inscrições Abertas + Em Andamento |
| DOE SP | Executivo | Busca textual por nome | Últimos 30 dias |

## Configuração

### 1. GitHub Secrets

| Secret | Descrição | Exemplo |
|---|---|---|
| `MEU_NOME` | Nome completo a ser buscado nos documentos | `Renan Bezerra dos Santos` |
| `PHONE` | Seu número de telefone com DDI (CallMeBot) | `5511999999999` |
| `API_KEY` | API key do CallMeBot | `123456` |

### 2. Configurar CallMeBot

1. Adicione o número `+34 644 71 84 58` nos seus contatos
2. Envie a mensagem `I allow callmebot to send me messages` via WhatsApp para esse número
3. Você receberá sua **apikey** em resposta

### 3. Configurar GitHub Secrets

No repositório GitHub, vá em **Settings → Secrets and variables → Actions** e adicione:

- `MEU_NOME`
- `PHONE`
- `API_KEY`

### 4. Execução

**Automática:** O GitHub Actions executa a cada 4 horas via cron.

**Manual:** Vá em **Actions → Tracker de Concursos ETEC/FATEC → Run workflow**.

**Local:**
```bash
pip install -r requirements.txt

export MEU_NOME="Renan Bezerra dos Santos"
export CALLMEBOT_PHONE="5511999999999"
export CALLMEBOT_APIKEY="sua_apikey"

python tracker_aprovacao.py
```

## Estrutura

```
├── tracker_aprovacao.py      # Crawler autônomo + analisador de documentos
├── requirements.txt          # Dependências Python
├── history_pdfs.json         # Histórico de documentos já processados (persistido pelo CI)
├── README.md
└── .github/
    └── workflows/
        └── tracker.yml       # GitHub Actions (cron a cada 4h)
```
