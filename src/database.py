import sqlite3
import pandas as pd
from .config import DATABASE_PATH

def conectar():
    return sqlite3.connect(DATABASE_PATH)

def inicializar():
    with conectar() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS precos (
            data_base TEXT NOT NULL,
            tipo_titulo TEXT NOT NULL,
            data_vencimento TEXT NOT NULL,
            taxa_compra REAL,
            taxa_venda REAL,
            preco_compra REAL,
            preco_venda REAL,
            preco_base REAL,
            taxa_compra_tarde REAL,
            taxa_venda_tarde REAL,
            preco_compra_tarde REAL,
            preco_venda_tarde REAL,
            chave TEXT PRIMARY KEY
        )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_titulo_data ON precos(tipo_titulo, data_base)")
        conn.commit()

def upsert_dataframe(df: pd.DataFrame) -> int:
    inicializar()
    cols = [
        "data_base", "tipo_titulo", "data_vencimento",
        "taxa_compra", "taxa_venda", "preco_compra", "preco_venda", "preco_base",
        "taxa_compra_tarde", "taxa_venda_tarde",
        "preco_compra_tarde", "preco_venda_tarde", "chave"
    ]
    work = df.copy()
    for c in cols:
        if c not in work.columns:
            work[c] = None

    work["data_base"] = pd.to_datetime(work["data_base"]).dt.strftime("%Y-%m-%d")
    work["data_vencimento"] = pd.to_datetime(work["data_vencimento"]).dt.strftime("%Y-%m-%d")

    sql = f"""INSERT OR REPLACE INTO precos ({",".join(cols)})
              VALUES ({",".join(["?"] * len(cols))})"""

    rows = work[cols].where(pd.notna(work[cols]), None).itertuples(index=False, name=None)
    rows = list(rows)

    with conectar() as conn:
        before = conn.execute("SELECT COUNT(*) FROM precos").fetchone()[0]
        conn.executemany(sql, rows)
        conn.commit()
        after = conn.execute("SELECT COUNT(*) FROM precos").fetchone()[0]
    return after - before

def consultar(titulo=None, vencimento=None, data_inicio=None, data_fim=None):
    inicializar()
    query = "SELECT * FROM precos WHERE 1=1"
    params = []

    if titulo:
        query += " AND tipo_titulo = ?"; params.append(titulo)
    if vencimento:
        query += " AND data_vencimento = ?"; params.append(str(vencimento))
    if data_inicio:
        query += " AND data_base >= ?"; params.append(str(data_inicio))
    if data_fim:
        query += " AND data_base <= ?"; params.append(str(data_fim))

    query += " ORDER BY data_base, tipo_titulo, data_vencimento"
    with conectar() as conn:
        return pd.read_sql_query(query, conn, params=params)

def listar_titulos():
    inicializar()
    with conectar() as conn:
        return pd.read_sql_query(
            "SELECT DISTINCT tipo_titulo FROM precos ORDER BY tipo_titulo", conn
        )["tipo_titulo"].tolist()

def listar_vencimentos(titulo=None):
    inicializar()
    query = "SELECT DISTINCT data_vencimento FROM precos"
    params = []
    if titulo:
        query += " WHERE tipo_titulo = ?"; params.append(titulo)
    query += " ORDER BY data_vencimento"
    with conectar() as conn:
        return pd.read_sql_query(query, conn, params=params)["data_vencimento"].tolist()
