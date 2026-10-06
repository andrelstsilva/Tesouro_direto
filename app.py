import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.database import inicializar, listar_titulos, listar_vencimentos, consultar
from src.analytics import preparar_serie, resumo

st.set_page_config(
    page_title="Tesouro Direto Analytics",
    page_icon="📊",
    layout="wide"
)

inicializar()

st.title("📊 Tesouro Direto Analytics")
st.caption("Dashboard de preços e taxas com dados oficiais do Tesouro Nacional.")

titulos = listar_titulos()

if not titulos:
    st.warning("Banco vazio. Execute primeiro: python -m src.pipeline")
    st.stop()

with st.sidebar:
    st.header("Filtros")
    titulo = st.selectbox("Título", titulos)

    vencimentos = listar_vencimentos(titulo)
    vencimento = st.selectbox("Vencimento", ["Todos"] + vencimentos)

    df0 = consultar(
        titulo=titulo,
        vencimento=None if vencimento == "Todos" else vencimento
    )

    if df0.empty:
        st.warning("Sem dados para os filtros selecionados.")
        st.stop()

    min_date = pd.to_datetime(df0["data_base"]).min().date()
    max_date = pd.to_datetime(df0["data_base"]).max().date()

    periodo = st.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(periodo, tuple) and len(periodo) == 2:
        data_inicio, data_fim = periodo
    else:
        data_inicio, data_fim = min_date, max_date

df = consultar(
    titulo=titulo,
    vencimento=None if vencimento == "Todos" else vencimento,
    data_inicio=data_inicio,
    data_fim=data_fim
)

df = preparar_serie(df)

if df.empty:
    st.warning("Sem dados no período.")
    st.stop()

r = resumo(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Preço de venda", f"R$ {r['preco_atual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
c2.metric("Taxa de venda", f"{r['taxa_atual']:.2f}%")
c3.metric("Variação no período", f"{r['variacao_periodo_pct']:.2f}%")
vol = r["volatilidade_anualizada_pct"]
c4.metric("Volatilidade anualizada", "N/D" if pd.isna(vol) else f"{vol:.2f}%")

st.subheader("Evolução do preço")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["data_base"], y=df["preco_compra"],
    mode="lines", name="Preço compra"
))
fig.add_trace(go.Scatter(
    x=df["data_base"], y=df["preco_venda"],
    mode="lines", name="Preço venda"
))
fig.add_trace(go.Scatter(
    x=df["data_base"], y=df["media_movel_20"],
    mode="lines", name="Média móvel 20 dias"
))
fig.update_layout(
    xaxis_title="Data",
    yaxis_title="Preço (R$)",
    hovermode="x unified",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Taxa")
    fig_taxa = go.Figure()
    fig_taxa.add_trace(go.Scatter(
        x=df["data_base"], y=df["taxa_compra"],
        mode="lines", name="Taxa compra"
    ))
    fig_taxa.add_trace(go.Scatter(
        x=df["data_base"], y=df["taxa_venda"],
        mode="lines", name="Taxa venda"
    ))
    fig_taxa.update_layout(
        xaxis_title="Data",
        yaxis_title="Taxa (%)",
        height=400
    )
    st.plotly_chart(fig_taxa, use_container_width=True)

with col2:
    st.subheader("Variação diária do preço")
    fig_var = go.Figure()
    fig_var.add_trace(go.Bar(
        x=df["data_base"],
        y=df["var_preco_dia_pct"],
        name="Variação diária"
    ))
    fig_var.update_layout(
        xaxis_title="Data",
        yaxis_title="Variação (%)",
        height=400
    )
    st.plotly_chart(fig_var, use_container_width=True)

st.subheader("Dados")

display_cols = [
    "data_base", "tipo_titulo", "data_vencimento",
    "taxa_compra", "taxa_venda",
    "preco_compra", "preco_venda",
    "var_preco_dia_pct", "var_preco_acum_pct",
    "volatilidade_20d"
]
display_cols = [c for c in display_cols if c in df.columns]

st.dataframe(
    df[display_cols].sort_values("data_base", ascending=False),
    use_container_width=True,
    hide_index=True
)
