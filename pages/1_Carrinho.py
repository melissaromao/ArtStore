import streamlit as st

from core import config, styles, table_storage

st.set_page_config(page_title="ArtStore — Carrinho", page_icon=":material/shopping_cart:", layout="wide")
styles.inject_base_styles()

st.sidebar.markdown("## :material/palette: ArtStore")
st.sidebar.page_link("app.py", label="Galeria", icon=":material/gallery_thumbnail:")
st.sidebar.page_link("pages/1_Carrinho.py", label="Carrinho", icon=":material/shopping_cart:")
st.sidebar.page_link("pages/2_Meus_Pedidos.py", label="Meus pedidos", icon=":material/inventory_2:")
st.sidebar.page_link("pages/3_Admin.py", label="Painel administrativo", icon=":material/admin_panel_settings:")

styles.hero("Seu carrinho", "Confira as obras selecionadas e finalize o pedido.")

erro_config = config.validar_configuracao()
if erro_config:
    st.error(erro_config)
    st.stop()

carrinho = st.session_state.get("carrinho", {})

if not carrinho:
    st.info("Seu carrinho está vazio. Volte à galeria para escolher uma obra.")
    st.page_link("app.py", label="Voltar à galeria", icon=":material/arrow_back:")
    st.stop()

total = 0.0
for row_key, item in list(carrinho.items()):
    produto = item["produto"]
    preco = float(produto.get("Preco", 0))
    subtotal = preco * item["quantidade"]
    total += subtotal

    col_img, col_info, col_qtd, col_rm = st.columns([1, 3, 1, 1])
    with col_img:
        st.image(produto.get("ImagemUrl") or "https://placehold.co/200x200?text=Sem+imagem", width=100)
    with col_info:
        st.markdown(f"**{produto.get('Titulo')}**  \n*{produto.get('Artista')}*")
        st.caption(f"R$ {preco:.2f} cada")
    with col_qtd:
        st.markdown(f"Qtd: **{item['quantidade']}**")
        st.markdown(f"Subtotal: **R$ {subtotal:.2f}**")
    with col_rm:
        if st.button("Remover", key=f"rm_{row_key}"):
            del st.session_state.carrinho[row_key]
            st.rerun()
    st.divider()

st.markdown(f"### Total: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

styles.section_title("Finalizar pedido")

with st.form("checkout_form"):
    st.markdown("#### Dados do cliente")
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome completo *")
        email = st.text_input("E-mail *")
    with c2:
        telefone = st.text_input("Telefone")
        cpf = st.text_input("CPF")

    st.markdown("#### Entrega")
    endereco = st.text_area("Endereço completo *")
    metodo_entrega = st.selectbox("Método de entrega", ["Retirada no ateliê", "Correios (PAC)", "Correios (SEDEX)", "Motoboy"])

    st.markdown("#### Pagamento")
    metodo_pagamento = st.selectbox("Forma de pagamento", ["Cartão de crédito", "Cartão de débito", "Pix", "Boleto"])

    enviado = st.form_submit_button("Confirmar pedido", use_container_width=True)

if enviado:
    campos_obrigatorios = [nome, email, endereco]
    if not all(campos_obrigatorios):
        st.error("Preencha nome, e-mail e endereço para concluir o pedido.")
        st.stop()

    itens_pedido = []
    erro_estoque = False
    for row_key, item in carrinho.items():
        produto_atual = table_storage.obter_produto(row_key)
        if not produto_atual:
            st.error(f"A obra “{item['produto'].get('Titulo')}” não está mais disponível.")
            erro_estoque = True
            continue
        estoque_atual = int(produto_atual.get("Quantidade", 0))
        if estoque_atual < item["quantidade"]:
            st.error(
                f"Estoque insuficiente para “{produto_atual.get('Titulo')}”. "
                f"Disponível: {estoque_atual}, solicitado: {item['quantidade']}."
            )
            erro_estoque = True
            continue
        preco_atual = float(produto_atual.get("Preco", 0))
        itens_pedido.append(
            {
                "RowKey": row_key,
                "Titulo": produto_atual.get("Titulo"),
                "Preco": preco_atual,
                "Quantidade": item["quantidade"],
                "Subtotal": preco_atual * item["quantidade"],
            }
        )

    if erro_estoque:
        st.stop()

    total_validado = sum(i["Subtotal"] for i in itens_pedido)

    cliente = table_storage.obter_cliente_por_email(email)
    if cliente:
        table_storage.atualizar_cliente(
            cliente["RowKey"],
            {"Nome": nome, "Telefone": telefone, "CPF": cpf, "Endereco": endereco},
        )
    else:
        table_storage.criar_cliente(
            {"Nome": nome, "Email": email, "Telefone": telefone, "CPF": cpf, "Endereco": endereco}
        )

    itens_resumo = "; ".join(f"{i['Titulo']} x{i['Quantidade']}" for i in itens_pedido)
    table_storage.criar_pedido(
        {
            "ClienteNome": nome,
            "ClienteEmail": email,
            "Itens": itens_resumo,
            "Total": total_validado,
            "MetodoPagamento": metodo_pagamento,
            "MetodoEntrega": metodo_entrega,
            "Endereco": endereco,
            "Status": "Novo",
        }
    )

    for item in itens_pedido:
        table_storage.decrementar_estoque(item["RowKey"], item["Quantidade"])

    st.session_state.carrinho = {}
    st.success(":material/celebration: Pedido confirmado com sucesso! Acompanhe em “Meus pedidos”.")
    st.balloons()
