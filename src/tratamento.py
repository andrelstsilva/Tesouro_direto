from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


# ============================================================
# MAPEAMENTO DOS NOMES DA FONTE PARA NOMES PADRONIZADOS
# ============================================================

ALIASES = {
    "tipo_titulo": {
        "tipo_titulo",
        "tipo titulo",
        "tipo título",
    },

    "data_vencimento": {
        "data_vencimento",
        "data vencimento",
        "data de vencimento",
    },

    "data_base": {
        "data_base",
        "data base",
    },

    "taxa_compra": {
        "taxa_compra",
        "taxa compra",
        "taxa compra manha",
        "taxa compra manhã",
    },

    "taxa_venda": {
        "taxa_venda",
        "taxa venda",
        "taxa venda manha",
        "taxa venda manhã",
    },

    "preco_compra": {
        "preco_compra",
        "preço compra",
        "pu compra",
        "pu compra manha",
        "pu compra manhã",
    },

    "preco_venda": {
        "preco_venda",
        "preço venda",
        "pu venda",
        "pu venda manha",
        "pu venda manhã",
    },

    "preco_base": {
        "preco_base",
        "preço base",
        "pu base",
        "pu base manha",
        "pu base manhã",
    },

    "taxa_compra_tarde": {
        "taxa_compra_tarde",
        "taxa compra tarde",
    },

    "taxa_venda_tarde": {
        "taxa_venda_tarde",
        "taxa venda tarde",
    },

    "preco_compra_tarde": {
        "preco_compra_tarde",
        "preço compra tarde",
        "pu compra tarde",
    },

    "preco_venda_tarde": {
        "preco_venda_tarde",
        "preço venda tarde",
        "pu venda tarde",
    },

    "preco_base_tarde": {
        "preco_base_tarde",
        "preço base tarde",
        "pu base tarde",
    },
}


# ============================================================
# NORMALIZAÇÃO DOS NOMES DAS COLUNAS
# ============================================================

def _normalizar_nome(nome: str) -> str:
    """
    Converte nomes diferentes para uma representação única.

    Exemplos:

    'Data_base'      -> 'data base'
    'Data Base'      -> 'data base'
    'DATA_BASE'      -> 'data base'
    'Data Vencimento'-> 'data vencimento'
    'PU Base Manha'  -> 'pu base manha'
    """

    nome = str(nome).strip().lower()

    # Remove acentos
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(
        caractere
        for caractere in nome
        if not unicodedata.combining(caractere)
    )

    # "_" vira espaço
    nome = nome.replace("_", " ")

    # Remove espaços duplicados
    nome = re.sub(r"\s+", " ", nome)

    return nome.strip()


def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte os nomes das colunas para o padrão interno do projeto.
    """

    df = df.copy()

    mapa_normalizado = {}

    for coluna in df.columns:
        nome_normalizado = _normalizar_nome(coluna)

        for nome_padrao, aliases in ALIASES.items():

            aliases_normalizados = {
                _normalizar_nome(alias)
                for alias in aliases
            }

            if nome_normalizado in aliases_normalizados:
                mapa_normalizado[coluna] = nome_padrao
                break

    df = df.rename(columns=mapa_normalizado)

    return df


# ============================================================
# CONVERSÃO DE NÚMEROS
# ============================================================

def _parse_numero(serie: pd.Series) -> pd.Series:
    """
    Converte números brasileiros e internacionais para float.

    Exemplos:

    '12,3456'      -> 12.3456
    '1.234,56'     -> 1234.56
    '1234.56'      -> 1234.56
    """

    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce")

    s = serie.astype("string").str.strip()

    # Remove espaços
    s = s.str.replace(" ", "", regex=False)

    def converter(valor):

        if pd.isna(valor):
            return None

        valor = str(valor)

        if not valor:
            return None

        # Caso brasileiro: 1.234,56
        if "," in valor and "." in valor:
            if valor.rfind(",") > valor.rfind("."):
                valor = valor.replace(".", "")
                valor = valor.replace(",", ".")

        # Caso brasileiro simples: 12,34
        elif "," in valor:
            valor = valor.replace(",", ".")

        try:
            return float(valor)

        except ValueError:
            return None

    return s.map(converter)


# ============================================================
# LEITURA DO CSV
# ============================================================

def carregar_csv(caminho: str | Path) -> pd.DataFrame:

    caminho = Path(caminho)

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ]

    separadores = [
        ";",
        ",",
    ]

    ultimo_erro = None

    for encoding in encodings:

        for separador in separadores:

            try:

                df = pd.read_csv(
                    caminho,
                    encoding=encoding,
                    sep=separador,
                    low_memory=False,
                )

                # Evita considerar leitura incorreta
                # com apenas uma coluna
                if len(df.columns) > 1:
                    return df

            except Exception as erro:

                ultimo_erro = erro

    raise ValueError(
        f"Não foi possível ler o arquivo CSV: {caminho}"
    ) from ultimo_erro


# ============================================================
# TRATAMENTO PRINCIPAL
# ============================================================

def tratar(df: pd.DataFrame) -> pd.DataFrame:

    if df is None or df.empty:
        raise ValueError("O DataFrame recebido está vazio.")

    df = df.copy()

    # --------------------------------------------------------
    # 1. PADRONIZA OS NOMES
    # --------------------------------------------------------

    df = padronizar_colunas(df)

    print("\nColunas após padronização:")
    print(list(df.columns))

    # --------------------------------------------------------
    # 2. COLUNAS OBRIGATÓRIAS
    # --------------------------------------------------------

    obrigatorias = [
        "tipo_titulo",
        "data_vencimento",
        "data_base",
        "taxa_compra",
        "taxa_venda",
        "preco_compra",
        "preco_venda",
        "preco_base",
    ]

    ausentes = [
        coluna
        for coluna in obrigatorias
        if coluna not in df.columns
    ]

    if ausentes:

        raise ValueError(
            "Colunas obrigatórias ausentes: "
            f"{ausentes}. "
            f"Encontradas: {list(df.columns)}"
        )

    # --------------------------------------------------------
    # 3. DATAS
    # --------------------------------------------------------

    df["data_base"] = pd.to_datetime(
        df["data_base"],
        errors="coerce",
        dayfirst=True,
    )

    df["data_vencimento"] = pd.to_datetime(
        df["data_vencimento"],
        errors="coerce",
        dayfirst=True,
    )

    # --------------------------------------------------------
    # 4. CAMPOS NUMÉRICOS
    # --------------------------------------------------------

    colunas_numericas = [
        "taxa_compra",
        "taxa_venda",
        "preco_compra",
        "preco_venda",
        "preco_base",
        "taxa_compra_tarde",
        "taxa_venda_tarde",
        "preco_compra_tarde",
        "preco_venda_tarde",
        "preco_base_tarde",
    ]

    for coluna in colunas_numericas:

        if coluna in df.columns:

            df[coluna] = _parse_numero(
                df[coluna]
            )

    # --------------------------------------------------------
    # 5. TEXTO
    # --------------------------------------------------------

    df["tipo_titulo"] = (
        df["tipo_titulo"]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # 6. REMOVER REGISTROS SEM CHAVES
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "tipo_titulo",
            "data_base",
            "data_vencimento",
        ]
    )

    # --------------------------------------------------------
    # 7. PREÇOS INVÁLIDOS
    # --------------------------------------------------------

    colunas_preco = [
        "preco_compra",
        "preco_venda",
        "preco_base",
    ]

    for coluna in colunas_preco:

        if coluna in df.columns:

            df.loc[
                df[coluna] <= 0,
                coluna
            ] = pd.NA

    # --------------------------------------------------------
    # 8. CRIAR CHAVE ÚNICA
    # --------------------------------------------------------

    df["chave"] = (
        df["data_base"].dt.strftime("%Y-%m-%d")
        + "|"
        + df["tipo_titulo"].astype(str)
        + "|"
        + df["data_vencimento"].dt.strftime("%Y-%m-%d")
    )

    # --------------------------------------------------------
    # 9. REMOVER DUPLICIDADES
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=["chave"],
        keep="last",
    )

    # --------------------------------------------------------
    # 10. ORDENAR
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "data_base",
            "tipo_titulo",
            "data_vencimento",
        ]
    ).reset_index(drop=True)

    return df


# ============================================================
# RELATÓRIO DE QUALIDADE
# ============================================================

def quality_report(df: pd.DataFrame) -> dict:

    if df.empty:

        return {
            "rows": 0,
            "columns": list(df.columns),
            "duplicate_keys": 0,
            "null_counts": {},
            "non_positive_prices": {},
        }

    duplicadas = 0

    if "chave" in df.columns:

        duplicadas = int(
            df["chave"].duplicated().sum()
        )

    colunas_preco = [
        "preco_compra",
        "preco_venda",
        "preco_base",
    ]

    nao_positivos = {}

    for coluna in colunas_preco:

        if coluna in df.columns:

            nao_positivos[coluna] = int(
                (df[coluna] <= 0).sum()
            )

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "duplicate_keys": duplicadas,
        "null_counts": (
            df.isna()
            .sum()
            .to_dict()
        ),
        "non_positive_prices": nao_positivos,
    }