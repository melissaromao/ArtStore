"""
ArtStore — E-commerce de venda de artes online
Página inicial: catálogo de obras, com busca por filtros e adição ao carrinho.
"""
import streamlit as st

from core import config, styles, table_storage

st.set_page_config(page_title="ArtStore — Galeria", page_icon=":material/palette:", layout="wide")
styles.inject_base_styles()

erro_config = config.validar_configuracao()

st.sidebar.markdown("## :material/palette: ArtStore")
st.sidebar.caption("Arte original, direto do ateliê para sua casa.")
st.sidebar.divider()
st.sidebar.page_link("app.py", label="Galeria", icon=":material/gallery_thumbnail:")
st.sidebar.page_link("pages/1_Carrinho.py", label="Carrinho", icon=":material/shopping_cart:")
st.sidebar.page_link("pages/2_Meus_Pedidos.py", label="Meus pedidos", icon=":material/inventory_2:")
st.sidebar.page_link("pages/3_Admin.py", label="Painel administrativo", icon=":material/admin_panel_settings:")

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}  # row_key -> {"produto": entity, "quantidade": int}

styles.hero(
    "Galeria ArtStore",
    "Descubra e compre obras originais de artistas independentes.",
)

if erro_config:
    st.error(erro_config)
    st.stop()

try:
    produtos = table_storage.listar_produtos()
except Exception as exc:
    st.error(f"Não foi possível conectar ao Azure Table Storage: {exc}")
    st.stop()

# ---------------------------------------------------------------------------
# Filtros
# ---------------------------------------------------------------------------
with st.expander(":material/search: Filtrar obras", expanded=True):
    col1, col2, col3 = st.columns(3)
    artistas = sorted({p.get("Artista", "") for p in produtos if p.get("Artista")})
    tecnicas = sorted({p.get("Tecnica", "") for p in produtos if p.get("Tecnica")})

    with col1:
        filtro_artista = st.selectbox("Artista", ["Todos"] + artistas)
    with col2:
        filtro_tecnica = st.selectbox("Técnica", ["Todas"] + tecnicas)
    with col3:
        precos = [float(p.get("Preco", 0)) for p in produtos] or [0]
        faixa = st.slider(
            "Faixa de preço (R$)",
            min_value=0.0,
            max_value=max(precos + [100.0]),
            value=(0.0, max(precos + [100.0])),
        )

produtos_filtrados = [
    p
    for p in produtos
    if (filtro_artista == "Todos" or p.get("Artista") == filtro_artista)
    and (filtro_tecnica == "Todas" or p.get("Tecnica") == filtro_tecnica)
    and faixa[0] <= float(p.get("Preco", 0)) <= faixa[1]
]

styles.section_title(f"Obras disponíveis ({len(produtos_filtrados)})")

if not produtos_filtrados:
    st.info("Nenhuma obra encontrada com os filtros selecionados.")
else:
    colunas = st.columns(3)
    for idx, produto in enumerate(produtos_filtrados):
        with colunas[idx % 3]:
            st.markdown(
                styles.art_card_html(
                    titulo=produto.get("Titulo", "Sem título"),
                    artista=produto.get("Artista", "Desconhecido"),
                    tecnica=produto.get("Tecnica", ""),
                    preco=produto.get("Preco", 0),
                    imagem_url=produto.get("ImagemUrl", ""),
                    dimensoes=produto.get("Dimensoes", ""),
                    quantidade=produto.get("Quantidade", 0),
                ),
                unsafe_allow_html=True,
            )
            quantidade_disponivel = int(produto.get("Quantidade", 0))
            if quantidade_disponivel > 0:
                qtd = st.number_input(
                    "Quantidade",
                    min_value=1,
                    max_value=quantidade_disponivel,
                    value=1,
                    key=f"qtd_{produto['RowKey']}",
                    label_visibility="collapsed",
                )
                if st.button("Adicionar ao carrinho", key=f"add_{produto['RowKey']}", use_container_width=True):
                    carrinho = st.session_state.carrinho
                    item = carrinho.get(produto["RowKey"], {"produto": produto, "quantidade": 0})
                    item["quantidade"] = min(quantidade_disponivel, item["quantidade"] + qtd)
                    item["produto"] = produto
                    carrinho[produto["RowKey"]] = item
                    st.success(f"“{produto.get('Titulo')}” adicionado ao carrinho.")
            else:
                st.button("Esgotado", key=f"esgotado_{produto['RowKey']}", disabled=True, use_container_width=True)
            st.write("")
