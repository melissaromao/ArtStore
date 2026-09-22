import streamlit as st

from core import blob_storage, config, styles, table_storage

st.set_page_config(page_title="ArtStore — Admin", page_icon=":material/admin_panel_settings:", layout="wide")
styles.inject_base_styles()

st.sidebar.markdown("## :material/palette: ArtStore")
st.sidebar.page_link("app.py", label="Galeria", icon=":material/gallery_thumbnail:")
st.sidebar.page_link("pages/1_Carrinho.py", label="Carrinho", icon=":material/shopping_cart:")
st.sidebar.page_link("pages/2_Meus_Pedidos.py", label="Meus pedidos", icon=":material/inventory_2:")
st.sidebar.page_link("pages/3_Admin.py", label="Painel administrativo", icon=":material/admin_panel_settings:")

styles.hero("Painel administrativo", "Gerencie obras, clientes e pedidos da loja.")

erro_config = config.validar_configuracao()
if erro_config:
    st.error(erro_config)
    st.stop()

if "admin_autenticado" not in st.session_state:
    st.session_state.admin_autenticado = False

if not st.session_state.admin_autenticado:
    with st.form("login_admin"):
        senha = st.text_input("Senha do administrador", type="password")
        entrar = st.form_submit_button("Entrar")
    if entrar:
        if senha == config.ADMIN_PASSWORD:
            st.session_state.admin_autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

col_logout = st.columns([5, 1])[1]
with col_logout:
    if st.button("Sair"):
        st.session_state.admin_autenticado = False
        st.rerun()

aba_produtos, aba_clientes, aba_pedidos = st.tabs([
    ":material/gallery_thumbnail: Produtos",
    ":material/person: Clientes",
    ":material/inventory_2: Pedidos",
])

with aba_produtos:
    styles.section_title("Cadastrar nova obra")
    with st.form("novo_produto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Título da obra *")
            artista = st.text_input("Artista *")
            tecnica = st.text_input("Técnica (ex: óleo sobre tela)")
        with c2:
            preco = st.number_input("Preço (R$) *", min_value=0.0, step=10.0)
            quantidade = st.number_input("Quantidade disponível *", min_value=0, step=1)
            dimensoes = st.text_input("Dimensões (ex: 60x80 cm)")
        imagem = st.file_uploader("Foto da obra", type=["png", "jpg", "jpeg", "webp"])
        criar = st.form_submit_button("Cadastrar obra", use_container_width=True)

    if criar:
        if not titulo or not artista or preco <= 0:
            st.error("Preencha ao menos título, artista e um preço válido.")
        else:
            imagem_url = ""
            if imagem is not None:
                try:
                    imagem_url = blob_storage.upload_image(
                        imagem.getvalue(), imagem.name, imagem.type or "image/jpeg"
                    )
                except Exception as exc:
                    st.error(f"Falha ao enviar imagem para o Blob Storage: {exc}")
                    st.stop()
            table_storage.criar_produto(
                {
                    "Titulo": titulo,
                    "Artista": artista,
                    "Tecnica": tecnica,
                    "Dimensoes": dimensoes,
                    "Preco": float(preco),
                    "Quantidade": int(quantidade),
                    "ImagemUrl": imagem_url,
                }
            )
            st.success(f"Obra “{titulo}” cadastrada com sucesso.")
            st.rerun()

    styles.section_title("Obras cadastradas")
    produtos = table_storage.listar_produtos()

    if not produtos:
        st.info("Nenhuma obra cadastrada ainda.")

    for produto in produtos:
        with st.expander(f"{produto.get('Titulo')} — {produto.get('Artista')}"):
            col_img, col_form = st.columns([1, 3])
            with col_img:
                st.image(produto.get("ImagemUrl") or "https://placehold.co/200x200?text=Sem+imagem", width=160)
                nova_imagem = st.file_uploader(
                    "Substituir imagem", type=["png", "jpg", "jpeg", "webp"], key=f"img_{produto['RowKey']}"
                )
            with col_form:
                with st.form(f"editar_{produto['RowKey']}"):
                    e1, e2 = st.columns(2)
                    with e1:
                        n_titulo = st.text_input("Título", value=produto.get("Titulo", ""))
                        n_artista = st.text_input("Artista", value=produto.get("Artista", ""))
                        n_tecnica = st.text_input("Técnica", value=produto.get("Tecnica", ""))
                    with e2:
                        n_preco = st.number_input("Preço (R$)", min_value=0.0, step=10.0, value=float(produto.get("Preco", 0)))
                        n_quantidade = st.number_input("Quantidade", min_value=0, step=1, value=int(produto.get("Quantidade", 0)))
                        n_dimensoes = st.text_input("Dimensões", value=produto.get("Dimensoes", ""))

                    bcol1, bcol2 = st.columns(2)
                    with bcol1:
                        salvar = st.form_submit_button(":material/save: Salvar alterações", use_container_width=True)
                    with bcol2:
                        excluir = st.form_submit_button(":material/delete: Excluir obra", use_container_width=True)

                if salvar:
                    dados_atualizados = {
                        "Titulo": n_titulo,
                        "Artista": n_artista,
                        "Tecnica": n_tecnica,
                        "Dimensoes": n_dimensoes,
                        "Preco": float(n_preco),
                        "Quantidade": int(n_quantidade),
                    }
                    if nova_imagem is not None:
                        try:
                            nova_url = blob_storage.upload_image(
                                nova_imagem.getvalue(), nova_imagem.name, nova_imagem.type or "image/jpeg"
                            )
                            blob_storage.delete_image(produto.get("ImagemUrl", ""))
                            dados_atualizados["ImagemUrl"] = nova_url
                        except Exception as exc:
                            st.error(f"Falha ao enviar nova imagem: {exc}")
                            st.stop()
                    table_storage.atualizar_produto(produto["RowKey"], dados_atualizados)
                    st.success("Obra atualizada.")
                    st.rerun()

                if excluir:
                    blob_storage.delete_image(produto.get("ImagemUrl", ""))
                    table_storage.excluir_produto(produto["RowKey"])
                    st.success("Obra excluída.")
                    st.rerun()

with aba_clientes:
    styles.section_title("Clientes cadastrados")
    clientes = table_storage.listar_clientes()

    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")

    for cliente in clientes:
        with st.expander(f"{cliente.get('Nome', 'Sem nome')} — {cliente.get('Email', '')}"):
            with st.form(f"editar_cliente_{cliente['RowKey']}"):
                c1, c2 = st.columns(2)
                with c1:
                    n_nome = st.text_input("Nome", value=cliente.get("Nome", ""))
                    n_telefone = st.text_input("Telefone", value=cliente.get("Telefone", ""))
                with c2:
                    n_cpf = st.text_input("CPF", value=cliente.get("CPF", ""))
                    n_endereco = st.text_area("Endereço", value=cliente.get("Endereco", ""))

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    salvar_cliente = st.form_submit_button(":material/save: Salvar", use_container_width=True)
                with bcol2:
                    excluir_cliente = st.form_submit_button(":material/delete: Excluir cliente", use_container_width=True)

            if salvar_cliente:
                table_storage.atualizar_cliente(
                    cliente["RowKey"],
                    {"Nome": n_nome, "Telefone": n_telefone, "CPF": n_cpf, "Endereco": n_endereco},
                )
                st.success("Cliente atualizado.")
                st.rerun()

            if excluir_cliente:
                table_storage.excluir_cliente(cliente["RowKey"])
                st.success("Cliente excluído.")
                st.rerun()

            styles.section_title("")
            pedidos_cliente = table_storage.listar_pedidos_por_cliente(cliente.get("Email", ""))
            st.caption(f"Histórico: {len(pedidos_cliente)} pedido(s) realizado(s).")

with aba_pedidos:
    styles.section_title("Todos os pedidos")
    pedidos = table_storage.listar_todos_pedidos()
    pedidos.sort(key=lambda p: p.get("CriadoEm", ""), reverse=True)

    if not pedidos:
        st.info("Nenhum pedido registrado ainda.")

    status_opcoes = ["Novo", "Em preparação", "Enviado", "Entregue", "Cancelado"]

    for pedido in pedidos:
        with st.expander(
            f"{pedido.get('ClienteNome', '-')} · R$ {float(pedido.get('Total', 0)):.2f} · {pedido.get('Status', 'Novo')}"
        ):
            st.write(f"**Cliente:** {pedido.get('ClienteNome')} ({pedido.get('ClienteEmail')})")
            st.write(f"**Itens:** {pedido.get('Itens')}")
            st.write(f"**Pagamento:** {pedido.get('MetodoPagamento')} · **Entrega:** {pedido.get('MetodoEntrega')}")
            st.write(f"**Endereço:** {pedido.get('Endereco')}")
            st.write(f"**Criado em:** {pedido.get('CriadoEm')}")

            status_atual = pedido.get("Status", "Novo")
            novo_status = st.selectbox(
                "Status do pedido",
                status_opcoes,
                index=status_opcoes.index(status_atual) if status_atual in status_opcoes else 0,
                key=f"status_{pedido['RowKey']}",
            )
            if st.button("Atualizar status", key=f"upd_{pedido['RowKey']}"):
                table_storage.atualizar_status_pedido(pedido["PartitionKey"], pedido["RowKey"], novo_status)
                st.success("Status atualizado.")
                st.rerun()
