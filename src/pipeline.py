import logging
from .coleta import baixar_dados
from .tratamento import carregar_csv, tratar, quality_report
from .database import inicializar, upsert_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def executar_pipeline():
    inicializar()
    logging.info("Iniciando coleta oficial.")
    arquivo = baixar_dados()
    bruto = carregar_csv(arquivo)
    tratado = tratar(bruto)
    qualidade = quality_report(tratado)

    logging.info("Qualidade: %s", qualidade)
    novos = upsert_dataframe(tratado)
    logging.info("Arquivo: %s", arquivo)
    logging.info("Linhas tratadas: %s", len(tratado))
    logging.info("Variação líquida no banco: %s", novos)
    return arquivo, tratado, novos, qualidade

if __name__ == "__main__":
    executar_pipeline()
