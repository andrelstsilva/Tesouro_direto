from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATABASE_DIR = BASE_DIR / "database"
OUTPUT_DIR = BASE_DIR / "outputs"
DATABASE_PATH = DATABASE_DIR / "tesouro.db"

# API pública CKAN do Tesouro Transparente.
CKAN_PACKAGE = (
    "https://www.tesourotransparente.gov.br/"
    "ckan/api/3/action/package_show"
    "?id=taxas-dos-titulos-ofertados-pelo-tesouro-direto"
)

for folder in [RAW_DIR, PROCESSED_DIR, DATABASE_DIR, OUTPUT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
