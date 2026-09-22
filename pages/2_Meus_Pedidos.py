import streamlit as st

from core import config, styles, table_storage

st.set_page_config(page_title="ArtStore — Meus Pedidos", page_icon=":material/inventory_2:", layout="wide")
styles.inject_base_styles()

st.sidebar.markdown("## :material/palette: ArtStore")
st.sidebar.page_link("app.py", label="Galeria", icon=":material/gallery_thumbnail:")
st.sidebar.page_link("pages/1_Carrinho.py", label="Carrinho", icon=":material/shopping_cart:")
st.sidebar.page_link("pages/2_Meus_Pedidos.py", label="Meus pedidos", icon=":material/inventory_2:")
st.sidebar.page_link("pages/3_Admin.py", label="Painel administrativo", icon=":material/admin_panel_settings:")

styles.hero("Área do cliente", "Consulte seus pedidos e mantenha seus dados atualizados.")

erro_config = config.validar_configuracao()
if erro_config:
    st.error(erro_config)
    st.stop()

email = st.text_input("Digite seu e-mail cadastrado para consultar seus pedidos")

if email:
    cliente = table_storage.obter_cliente_por_email(email)

    if not cliente:
        st.warning("Nenhum cliente encontrado com esse e-mail. Faça uma compra para se cadastrar automaticamente.")
    else:
        styles.section_title("Meus dados")
        with st.form("editar_cliente"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome", value=cliente.get("Nome", ""))
                telefone = st.text_input("Telefone", value=cliente.get("Telefone", ""))
            with c2:
                cpf = st.text_input("CPF", value=cliente.get("CPF", ""))
                endereco = st.text_area("Endereço", value=cliente.get("Endereco", ""))
            salvar = st.form_submit_button("Salvar alterações")
        if salvar:
            table_storage.atualizar_cliente(
                cliente["RowKey"],
                {"Nome": nome, "Telefone": telefone, "CPF": cpf, "Endereco": endereco},
            )
            st.success("Dados atualizados com sucesso.")

        styles.section_title("Histórico de pedidos")
        pedidos = table_storage.listar_pedidos_por_cliente(email)
        pedidos.sort(key=lambda p: p.get("CriadoEm", ""), reverse=True)

        if not pedidos:
            st.info("Você ainda não fez nenhum pedido.")
        else:
            for pedido in pedidos:
                status = pedido.get("Status", "Novo")
                cor = {
                    "Novo": "color3",
                    "Em preparação": "color5",
                    "Enviado": "color4",
                    "Entregue": "color4",
                    "Cancelado": "color2",
                }.get(status, "color5")
                st.markdown(
                    f"""
                    <div class="color5 border border-color4 rounded-2xl p-4 mb-3">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-xs">Pedido em {pedido.get('CriadoEm', '')[:10]}</span>
                            <span class="{cor} text-xs font-semibold px-2.5 py-1 rounded-full">{status}</span>
                        </div>
                        <p>{pedido.get('Itens', '')}</p>
                        <p class="text-sm mt-1">
                            Pagamento: {pedido.get('MetodoPagamento', '-')} · Entrega: {pedido.get('MetodoEntrega', '-')}
                        </p>
                        <p class="font-bold text-lg mt-2">
                            Total: R$ {float(pedido.get('Total', 0)):.2f}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
