# Tesouro Direto Analytics

Projeto de **Data Analytics end-to-end** para preços e taxas dos títulos públicos ofertados pelo Tesouro Direto.

## Objetivo de portfólio

Demonstrar competências de Analista de Dados:

- Python;
- ETL/ELT;
- consumo de API pública;
- Pandas;
- tratamento e qualidade de dados;
- SQL/SQLite;
- análise de séries temporais;
- KPIs;
- visualização interativa;
- Streamlit;
- exportação Excel;
- testes automatizados;
- arquitetura modular.

## Fonte oficial

Tesouro Transparente — Taxas dos Títulos Ofertados pelo Tesouro Direto.

O conjunto oficial informa atualização diária, dados desde janeiro de 2002 e disponibiliza preços e taxas de compra e venda.

## Indicadores

- preço de compra;
- preço de venda;
- preço-base;
- taxa de compra;
- taxa de venda;
- variação diária;
- variação acumulada;
- média móvel de 20 dias;
- volatilidade anualizada;
- máxima e mínima do período.

## Arquitetura

```text
API CKAN oficial
       |
       v
    COLETA
       |
       v
  CSV RAW
       |
       v
 TRATAMENTO
       |
       +----> DATA QUALITY
       |
       v
   SQLITE
       |
       v
  ANALYTICS
       |
       +----> Excel
       |
       +----> Dashboard Streamlit
       |
       +----> Power BI (próxima etapa)
```

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Executar ETL

Na raiz do projeto:

```powershell
python -m src.pipeline
```

## Executar dashboard

```powershell
streamlit run app.py
```
```Direto do navegador 
https://tesourodireto.streamlit.app
```

## Testes

Instale pytest se necessário:

```powershell
pip install pytest
```

Execute:

```powershell
pytest
```

## Exportar Excel

Exemplo:

```python
from src.database import consultar
from src.relatorio import exportar_excel

df = consultar(titulo="Tesouro Selic")
arquivo = exportar_excel(df)
print(arquivo)
```

## Power BI

A tabela SQLite `precos` foi estruturada para servir como camada analítica. O próximo passo é criar uma camada dimensional:

- `dim_titulo`
- `dim_data`
- `fato_precos`

Isso facilita modelagem em estrela e integração com Power BI.

## Boas práticas

O projeto não trata os indicadores como recomendação de investimento. Preços e taxas são dados de mercado e devem ser interpretados no contexto do título, vencimento e período.

## Fonte

https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
