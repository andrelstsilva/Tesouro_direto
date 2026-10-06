from datetime import datetime
from pathlib import Path
import requests
from .config import CKAN_PACKAGE, RAW_DIR

def obter_url_csv() -> str:
    response = requests.get(CKAN_PACKAGE, timeout=60)
    response.raise_for_status()
    payload = response.json()

    if not payload.get("success"):
        raise RuntimeError("A API CKAN não retornou success=True.")

    resources = payload["result"]["resources"]
    csvs = [
        r for r in resources
        if str(r.get("format", "")).upper() == "CSV"
        and r.get("url")
    ]
    if not csvs:
        raise RuntimeError("Nenhum recurso CSV foi encontrado na API oficial.")

    return csvs[0]["url"]

def baixar_dados() -> Path:
    url = obter_url_csv()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = RAW_DIR / f"tesouro_{stamp}.csv"

    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destino.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    return destino
