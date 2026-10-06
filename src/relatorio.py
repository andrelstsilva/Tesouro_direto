from pathlib import Path
import pandas as pd
from .config import OUTPUT_DIR
from .analytics import preparar_serie

def exportar_excel(df: pd.DataFrame, nome="tesouro_analytics.xlsx") -> Path:
    caminho = OUTPUT_DIR / nome
    serie = preparar_serie(df)
    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        serie.to_excel(writer, sheet_name="dados_analiticos", index=False)
        pd.DataFrame([{
            "linhas": len(serie),
            "data_min": serie["data_base"].min() if not serie.empty else None,
            "data_max": serie["data_base"].max() if not serie.empty else None,
            "preco_min": serie["preco_venda"].min() if not serie.empty else None,
            "preco_max": serie["preco_venda"].max() if not serie.empty else None,
        }]).to_excel(writer, sheet_name="resumo", index=False)
    return caminho
