import pandas as pd
import numpy as np

def preparar_serie(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["data_base"] = pd.to_datetime(df["data_base"])
    for col in ["preco_compra", "preco_venda", "taxa_compra", "taxa_venda"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("data_base")
    df["var_preco_dia_pct"] = df["preco_venda"].pct_change() * 100
    df["var_preco_acum_pct"] = (
        (df["preco_venda"] / df["preco_venda"].iloc[0]) - 1
    ) * 100

    df["media_movel_20"] = df["preco_venda"].rolling(20, min_periods=5).mean()
    df["volatilidade_20d"] = (
        df["var_preco_dia_pct"].rolling(20, min_periods=5).std()
        * np.sqrt(252)
    )
    return df

def resumo(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    serie = preparar_serie(df)
    ultimo = serie.iloc[-1]
    primeiro = serie.iloc[0]

    return {
        "preco_atual": ultimo.get("preco_venda"),
        "taxa_atual": ultimo.get("taxa_venda"),
        "variacao_periodo_pct": ultimo.get("var_preco_acum_pct"),
        "max_preco": serie["preco_venda"].max(),
        "min_preco": serie["preco_venda"].min(),
        "volatilidade_anualizada_pct": serie["volatilidade_20d"].iloc[-1],
        "data_atual": ultimo["data_base"],
        "data_inicial": primeiro["data_base"],
    }
