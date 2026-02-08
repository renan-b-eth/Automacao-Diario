# 🎯 Bot de Rastreamento de Concursos ETEC/FATEC

Bot pessoal em Python que monitora páginas de editais do CPS (URH) em busca de novos PDFs publicados e verifica automaticamente se o seu nome aparece nos documentos. Notificações via WhatsApp (CallMeBot).

## Como funciona

1. Acessa cada URL de edital configurada
2. Identifica todos os links de PDF na página
3. Compara com `history_pdfs.json` para detectar novos arquivos
4. Baixa PDFs novos **na memória** e extrai o texto com `pdfplumber`
5. Busca pelo seu nome (case insensitive)
6. Envia notificação via WhatsApp:
   - 🚨 **Nome encontrado** → alerta de aprovação/convocação
   - ⚠️ **Arquivo novo sem nome** → alerta de nova movimentação

## Configuração

### 1. Variáveis de ambiente / GitHub Secrets

| Variável | Descrição | Exemplo |
|---|---|---|
| `MEU_NOME` | Nome completo a ser buscado nos PDFs | `Renan Bezerra dos Santos` |
| `URLS_EDITAIS` | URLs das páginas de acompanhamento, separadas por vírgula | `https://urhsistemas.cps.sp.gov.br/...` |
| `CALLMEBOT_PHONE` | Seu número de telefone (com DDI) | `5511999999999` |
| `CALLMEBOT_APIKEY` | API key do CallMeBot | `123456` |

### 2. Configurar CallMeBot

1. Adicione o número `+34 644 71 84 58` nos seus contatos
2. Envie a mensagem `I allow callmebot to send me messages` via WhatsApp para esse número
3. Você receberá sua **apikey** em resposta

### 3. Configurar GitHub Secrets

No repositório GitHub, vá em **Settings → Secrets and variables → Actions** e adicione:

- `MEU_NOME`
- `URLS_EDITAIS`
- `CALLMEBOT_PHONE`
- `CALLMEBOT_APIKEY`

### 4. Execução

**Automática:** O GitHub Actions executa a cada 4 horas via cron.

**Manual:** Vá em **Actions → Tracker de Concursos ETEC/FATEC → Run workflow**.

**Local:**
```bash
pip install -r requirements.txt

export MEU_NOME="Renan Bezerra dos Santos"
export URLS_EDITAIS="https://url1.com,https://url2.com"
export CALLMEBOT_PHONE="5511999999999"
export CALLMEBOT_APIKEY="sua_apikey"

python tracker_aprovacao.py
```

## Estrutura

```
├── tracker_aprovacao.py      # Script principal
├── requirements.txt          # Dependências Python
├── history_pdfs.json         # Histórico de PDFs já processados (persistido pelo CI)
├── README.md
└── .github/
    └── workflows/
        └── tracker.yml       # GitHub Actions (cron a cada 4h)
```
