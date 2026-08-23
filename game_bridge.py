"""
Ponte entre o motor do jogo (caso001.py) e uma interface interativa (web ou
outra). Não duplica nenhuma regra de jogo — reaproveita caso001.py 100% como
está, só substitui os pontos de entrada/saída (pausa, escolha, escolha_
agrupada, print) por versões que conseguem "pausar" a execução no meio de
uma função Python comum.

Como funciona (padrão de replay determinístico):
- caso001.py nunca usa aleatoriedade — dada a mesma sequência de respostas,
  ele sempre pede as mesmas perguntas, na mesma ordem.
- A cada interação da pessoa jogando, rodamos o jogo inteiro DE NOVO desde o
  início, "reproduzindo" automaticamente todas as respostas já dadas antes.
  Quando a lista de respostas acaba, a próxima chamada a escolha()/pausa()
  não tem o que devolver — nesse ponto, levantamos NeedInput, que interrompe
  a execução exatamente ali. É esse ponto que a interface mostra para a
  pessoa responder.
- Isso evita qualquer duplicação de lógica de estado: o estado do jogo
  (E, evidências, prazos, finais) é sempre recalculado pelo próprio
  caso001.py, nunca reimplementado aqui.
"""

import caso001 as game


class NeedInput(Exception):
    """Levantada quando o replay chega ao fim da lista de respostas já
    dadas e o jogo precisa de mais uma para continuar."""

    def __init__(self, kind, titulo=None, opcoes=None, grupos=None):
        self.kind = kind        # 'pausa' | 'escolha' | 'escolha_agrupada'
        self.titulo = titulo
        self.opcoes = opcoes    # lista de strings, para 'escolha'
        self.grupos = grupos    # lista de (rotulo, [strings]), para 'escolha_agrupada'
        super().__init__(kind)


class _Replayer:
    """Repositor de respostas: entrega, em ordem, as respostas já registradas
    nesta partida; quando acabam, levanta NeedInput."""

    def __init__(self, respostas):
        self._respostas = respostas
        self._pos = 0

    def proxima(self, kind, **info):
        if self._pos < len(self._respostas):
            kind_gravado, valor = self._respostas[self._pos]
            self._pos += 1
            if kind_gravado != kind:
                # Não deveria acontecer (o jogo é determinístico), mas se a
                # lista de respostas ficou inconsistente é melhor falhar
                # de forma clara do que silenciosamente dar a resposta errada.
                raise RuntimeError(
                    f"Histórico de respostas inconsistente: esperava "
                    f"'{kind_gravado}', o jogo pediu '{kind}'."
                )
            return valor
        raise NeedInput(kind, **info)


def rodar_partida(respostas):
    """Roda caso001.py do zero, repondo automaticamente `respostas`
    (lista de tuplas (kind, valor)) e parando no ponto exato em que a
    próxima resposta ainda não existe.

    Retorna um dicionário:
      - transcript: lista de strings (tudo que o jogo "imprimiu" até aqui)
      - pending: None (jogo esperando o fim) ou um NeedInput com o que falta
      - fim_de_jogo: bool
      - estado: o objeto Estado (game.E) já populado, para ler resumo/prazos
    """
    game.E = game.Estado()
    replayer = _Replayer(respostas)
    transcript = []

    def st_print(*args, **kwargs):
        texto = " ".join(str(a) for a in args)
        transcript.append(texto)

    def st_pausa():
        replayer.proxima('pausa')

    def st_escolha(titulo, opcoes):
        valor = replayer.proxima('escolha', titulo=titulo, opcoes=opcoes)
        return int(valor)

    def st_escolha_agrupada(titulo, grupos):
        valor = replayer.proxima('escolha_agrupada', titulo=titulo, grupos=grupos)
        return int(valor)

    game.print = st_print
    game.pausa = st_pausa
    game.escolha = st_escolha
    game.escolha_agrupada = st_escolha_agrupada

    pending = None
    try:
        game.main()
        fim_de_jogo = True
    except NeedInput as ni:
        pending = ni
        fim_de_jogo = False

    return {
        "transcript": transcript,
        "pending": pending,
        "fim_de_jogo": fim_de_jogo,
        "estado": game.E,
    }


def resumo_do_estado():
    """Reaproveita game.mostrar_resumo() (que só usa print) para gerar o
    texto do painel de resumo, sem misturar esse conteúdo com o transcript
    principal da partida."""
    linhas = []

    def capturar(*args, **kwargs):
        linhas.append(" ".join(str(a) for a in args))

    original = game.print
    game.print = capturar
    try:
        game.mostrar_resumo()
    finally:
        game.print = original
    return "\n".join(linhas)
