#!/usr/bin/env python3
"""
Bot de Rastreamento de Concursos ETEC/FATEC
Monitora páginas de editais do CPS (URH) em busca de novos PDFs
e verifica se o nome do candidato aparece nos documentos.

Notificações via WhatsApp (CallMeBot).
"""

import io
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import pdfplumber
import requests
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────
# CONFIGURAÇÃO
# ──────────────────────────────────────────────

MEU_NOME = os.getenv("MEU_NOME", "Renan Bezerra dos Santos")

# URLs das páginas de acompanhamento (separadas por vírgula na env var)
_urls_env = os.getenv("URLS_EDITAIS", "")
URLS_EDITAIS: list[str] = [u.strip() for u in _urls_env.split(",") if u.strip()]

# CallMeBot – WhatsApp
CALLMEBOT_PHONE = os.getenv("CALLMEBOT_PHONE", "")
CALLMEBOT_APIKEY = os.getenv("CALLMEBOT_APIKEY", "")

# Caminho do histórico de PDFs já processados
HISTORY_FILE = Path(__file__).parent / "history_pdfs.json"

# Headers para simular navegador comum
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 30  # segundos


# ──────────────────────────────────────────────
# HISTÓRICO
# ──────────────────────────────────────────────

def load_history() -> dict:
    """Carrega o JSON com os PDFs já processados."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history: dict) -> None:
    """Salva o JSON atualizado."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# NOTIFICAÇÃO – WHATSAPP (CallMeBot)
# ──────────────────────────────────────────────

def send_whatsapp(message: str) -> None:
    """Envia mensagem via CallMeBot WhatsApp API."""
    if not CALLMEBOT_PHONE or not CALLMEBOT_APIKEY:
        print("[AVISO] CallMeBot não configurado. Mensagem apenas no log:")
        print(message)
        return

    url = "https://api.callmebot.com/whatsapp.php"
    params = {
        "phone": CALLMEBOT_PHONE,
        "text": message,
        "apikey": CALLMEBOT_APIKEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            print("[OK] Mensagem WhatsApp enviada.")
        else:
            print(f"[ERRO] CallMeBot retornou status {resp.status_code}: {resp.text}")
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao enviar WhatsApp: {e}")

    # Respeitar rate-limit do CallMeBot (mín. 2 s entre mensagens)
    time.sleep(3)


# ──────────────────────────────────────────────
# SCRAPING
# ──────────────────────────────────────────────

def fetch_pdf_links(page_url: str) -> list[dict]:
    """
    Acessa a página do edital e retorna uma lista de dicts:
    [{"name": "nome_do_arquivo.pdf", "url": "https://..."}]
    """
    try:
        resp = requests.get(page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERRO] Não foi possível acessar {page_url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    pdf_links: list[dict] = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if re.search(r"\.pdf(\?.*)?$", href, re.IGNORECASE):
            full_url = urljoin(page_url, href)
            name = a_tag.get_text(strip=True) or href.split("/")[-1].split("?")[0]
            pdf_links.append({"name": name, "url": full_url})

    return pdf_links


# ──────────────────────────────────────────────
# ANÁLISE DE PDF
# ──────────────────────────────────────────────

def check_name_in_pdf(pdf_url: str, name: str) -> bool:
    """Baixa o PDF na memória e verifica se o nome aparece (case insensitive)."""
    try:
        resp = requests.get(pdf_url, headers=HEADERS, timeout=REQUEST_TIMEOUT * 2)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERRO] Falha ao baixar PDF {pdf_url}: {e}")
        return False

    name_lower = name.lower()
    try:
        with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if name_lower in text.lower():
                    return True
    except Exception as e:
        print(f"  [ERRO] Falha ao ler PDF {pdf_url}: {e}")

    return False


# ──────────────────────────────────────────────
# LÓGICA PRINCIPAL
# ──────────────────────────────────────────────

def process_edital(page_url: str, history: dict) -> dict:
    """
    Processa uma página de edital.
    Retorna o history atualizado.
    """
    print(f"\n{'='*60}")
    print(f"Verificando: {page_url}")
    print(f"{'='*60}")

    pdf_links = fetch_pdf_links(page_url)
    if not pdf_links:
        print("  Nenhum PDF encontrado na página.")
        return history

    print(f"  {len(pdf_links)} PDF(s) encontrado(s) na página.")

    for pdf_info in pdf_links:
        pdf_url = pdf_info["url"]
        pdf_name = pdf_info["name"]

        if pdf_url in history:
            print(f"  [SKIP] Já processado: {pdf_name}")
            continue

        print(f"  [NOVO] Analisando: {pdf_name}")
        found = check_name_in_pdf(pdf_url, MEU_NOME)

        # Registrar no histórico
        history[pdf_url] = {
            "name": pdf_name,
            "page": page_url,
            "found_name": found,
        }

        if found:
            msg = (
                "🚨 *PARABÉNS! SEU NOME FOI CITADO!* 🚨\n"
                f"📄 *Arquivo:* {pdf_name}\n"
                f"🔗 *Link:* {pdf_url}\n"
                f"🏫 *Concurso:* {page_url}"
            )
            print(f"  >>> NOME ENCONTRADO! <<<")
        else:
            msg = (
                "⚠️ *Nova Publicação no Concurso*\n"
                f"O arquivo '{pdf_name}' saiu, mas seu nome não foi "
                "encontrado na busca automática. Vale conferir.\n"
                f"🔗 *Link:* {pdf_url}\n"
                f"🏫 *Concurso:* {page_url}"
            )
            print(f"  Nome NÃO encontrado neste arquivo.")

        send_whatsapp(msg)

    return history


def main() -> None:
    if not URLS_EDITAIS:
        print("[ERRO] Nenhuma URL configurada em URLS_EDITAIS.")
        print("Defina a variável de ambiente URLS_EDITAIS com as URLs separadas por vírgula.")
        sys.exit(1)

    print(f"Bot de Rastreamento de Concursos ETEC/FATEC")
    print(f"Nome monitorado: {MEU_NOME}")
    print(f"URLs monitoradas: {len(URLS_EDITAIS)}")

    history = load_history()

    for url in URLS_EDITAIS:
        history = process_edital(url, history)

    save_history(history)
    print(f"\nHistórico salvo em {HISTORY_FILE}")
    print("Execução finalizada.")


if __name__ == "__main__":
    main()
