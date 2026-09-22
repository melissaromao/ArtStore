import streamlit as st


def inject_base_styles():
    st.markdown(
        """
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            :root {
                --color1: #fcf7d7;
                --color2: #fea667;
                --color3: #ffe461;
                --color4: #c4c776;
                --color5: #f4d092;
                --ink: #4a3b2a;
            }

            .color1 { background-color: var(--color1); }
            .color2 { background-color: var(--color2); }
            .color3 { background-color: var(--color3); }
            .color4 { background-color: var(--color4); }
            .color5 { background-color: var(--color5); }
            .border-color2 { border-color: var(--color2); }
            .border-color4 { border-color: var(--color4); }

            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header[data-testid="stHeader"] {background: var(--color1);}

            .stApp {
                background: var(--color1);
            }

            section[data-testid="stSidebar"] {
                background: var(--color4);
                border-right: 1px solid var(--color2);
            }
            section[data-testid="stSidebar"] * { color: var(--ink); }

            h1, h2, h3, h4, p, span, label, div { color: var(--ink); }

            .stButton>button {
                background: var(--color2);
                color: var(--ink);
                border: none;
                border-radius: 0.75rem;
                padding: 0.55rem 1.3rem;
                font-weight: 600;
                letter-spacing: .01em;
                transition: transform .15s ease, box-shadow .15s ease;
                box-shadow: 0 4px 14px rgba(74, 59, 42, 0.18);
            }
            .stButton>button:hover {
                transform: translateY(-1px);
                background: var(--color3);
                box-shadow: 0 6px 20px rgba(74, 59, 42, 0.25);
            }

            input, textarea, .stNumberInput input, .stTextInput input {
                border-radius: 0.6rem !important;
                background-color: var(--color5) !important;
                color: var(--ink) !important;
                border: 1px solid var(--color4) !important;
            }

            div[data-testid="stMetric"] {
                background: var(--color5);
                border: 1px solid var(--color4);
                border-radius: 1rem;
                padding: 1rem;
            }

            div[data-baseweb="tab-list"] { gap: 4px; }

            hr { border-color: var(--color4); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="w-full py-10 px-6 mb-6 rounded-3xl
                color5 border border-color4">
            <h1 class="text-4xl font-extrabold tracking-tight mb-2">{title}</h1>
            <p class="text-lg">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def art_card_html(titulo, artista, tecnica, preco, imagem_url, dimensoes="", quantidade=0):
    try:
        disponivel = int(quantidade) > 0
    except (TypeError, ValueError):
        disponivel = False

    badge = (
        '<span class="color3 text-xs font-semibold px-2.5 py-1 rounded-full">Disponível</span>'
        if disponivel
        else '<span class="color2 text-xs font-semibold px-2.5 py-1 rounded-full">Esgotado</span>'
    )
    img = imagem_url or "https://placehold.co/500x500/f4d092/4a3b2a?text=Sem+imagem"
    dims_html = f'<span class="text-sm">· {dimensoes}</span>' if dimensoes else ""

    try:
        preco_fmt = f"{float(preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        preco_fmt = str(preco)

    return f"""
    <div class="color5 border border-color4 rounded-2xl overflow-hidden
                shadow-lg hover:shadow-2xl hover:border-color2
                transition-all duration-200 h-full flex flex-col">
        <img src="{img}" class="w-full h-64 object-cover" />
        <div class="p-4 flex flex-col gap-1 flex-1">
            <div class="flex justify-between items-start gap-2">
                <h3 class="font-semibold text-lg leading-tight">{titulo}</h3>
                {badge}
            </div>
            <p class="text-sm font-medium">por {artista}</p>
            <p class="text-xs">{tecnica} {dims_html}</p>
            <div class="mt-3 pt-3 border-t border-color4 flex items-center justify-between">
                <span class="font-bold text-2xl">R$ {preco_fmt}</span>
                <span class="text-xs">{quantidade} un.</span>
            </div>
        </div>
    </div>
    """


def section_title(text: str):
    st.markdown(
        f'<h2 class="text-2xl font-bold mt-2 mb-4 border-l-4 '
        f'border-color2 pl-3">{text}</h2>',
        unsafe_allow_html=True,
    )
