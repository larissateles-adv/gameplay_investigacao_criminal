"""
Interface web do Caso 001 — O Apartamento 804.

Esta camada NÃO reimplementa nenhuma regra do jogo. Toda a lógica de estado,
prazos, evidências e finais continua vivendo em caso001.py. Este arquivo só
desenha a tela e traduz cliques em respostas, usando game_bridge.py para
rodar o motor original a cada interação.
"""

import streamlit as st

import game_bridge as gb

st.set_page_config(
    page_title="O Apartamento 804",
    page_icon="🔎",
    layout="centered",
)

if "respostas" not in st.session_state:
    st.session_state.respostas = []


def reiniciar():
    st.session_state.respostas = []


def responder(kind, valor):
    st.session_state.respostas.append((kind, valor))
    st.rerun()


# ---------------------------------------------------------------------------
# Roda o motor do jogo com o histórico de respostas atual
# ---------------------------------------------------------------------------

resultado = gb.rodar_partida(st.session_state.respostas)
transcript = resultado["transcript"]
pending = resultado["pending"]
fim_de_jogo = resultado["fim_de_jogo"]
estado = resultado["estado"]

# ---------------------------------------------------------------------------
# Barra lateral — resumo do caso, sempre visível, sem custar tempo do jogo
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### Resumo do caso")
    if st.session_state.respostas:
        resumo_texto = gb.resumo_do_estado()
        st.text(resumo_texto)
    else:
        st.caption("O resumo aparece assim que a investigação começar.")
    st.divider()
    if st.button("🔄 Recomeçar partida"):
        reiniciar()
        st.rerun()

# ---------------------------------------------------------------------------
# Corpo principal — transcript da história até agora
# ---------------------------------------------------------------------------

st.title("🔎 O Apartamento 804")
st.caption("Caso 001 — investigação criminal")

with st.container():
    for bloco in transcript:
        bloco = bloco.strip()
        if not bloco:
            continue
        if set(bloco) <= {"=", "-"}:
            continue  # separadores puramente visuais do modo terminal
        if bloco.startswith("0. Ver resumo do caso"):
            continue  # a opção de resumo virou o painel lateral
        st.markdown(bloco)

st.divider()

# ---------------------------------------------------------------------------
# Ponto de interação — o que a pessoa jogando faz agora
# ---------------------------------------------------------------------------

if fim_de_jogo:
    st.success("Fim de jogo.")
    if st.button("Jogar de novo"):
        reiniciar()
        st.rerun()

elif pending.kind == "pausa":
    st.button("Continuar ➜", on_click=lambda: responder("pausa", None))

elif pending.kind == "escolha":
    st.subheader(pending.titulo)
    for i, texto_opcao in enumerate(pending.opcoes, start=1):
        st.button(
            f"{i}. {texto_opcao}",
            key=f"escolha-{len(st.session_state.respostas)}-{i}",
            on_click=responder,
            args=("escolha", i),
        )

elif pending.kind == "escolha_agrupada":
    st.subheader(pending.titulo)
    contador = 1
    for rotulo, opcoes in pending.grupos:
        if not opcoes:
            continue
        st.markdown(f"**{rotulo}**")
        for texto_opcao in opcoes:
            st.button(
                f"{contador}. {texto_opcao}",
                key=f"escolhaag-{len(st.session_state.respostas)}-{contador}",
                on_click=responder,
                args=("escolha_agrupada", contador),
            )
            contador += 1
