#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CASO 001 — O Apartamento 804
Protótipo jogável em terminal (v1.1), baseado no Mapa de Ramificações v2.1.

Como jogar:
- Em cada momento, um menu numerado aparece. Digite o número da opção e Enter.
- A opção "0" mostra o resumo do caso (dias, provas, pilares, suspeitos) a
  qualquer momento, sem gastar tempo do inquérito.
- A verdade objetiva do caso é fixa e nunca aparece neste arquivo em texto
  simples de forma que o jogador possa lê-la por acidente rodando o jogo —
  ela só se revela através do que o jogador descobre jogando.

Mudanças da v1.1 em relação à v1 (revisão de fidelidade ao Mapa v2.1):
- Cena 3 (Seção 3) implementada: círculo pessoal x profissional/afetivo, em
  duas decisões binárias em sequência, antes de abrir o menu livre.
- Sistema de mini-aula jurídica (Seção 17): cada medida jurídica (sigilo
  telefônico, amostra biológica, DNA, digital, sigilo de dados, interceptação,
  tipo de prisão, cautelar diversa) agora mostra uma explicação curta da
  autoridade responsável antes de confirmar o pedido.
- Glossário embutido nas opções de menu das medidas jurídicas (Seção 8).
- Laudo pericial da fechadura de trinco automático agora é uma diligência
  pedível (fechava o Pilar 4 só "no papel" antes; era conteúdo inalcançável).
- Seção 15.1: se Rafael ou Camila forem presos por engano e o álibi aparecer
  durante a custódia, agora são soltos na hora, em vez de só ao fim do prazo.
- Corrigido: "Procurar Beatriz Lemos" não fica mais preso no menu depois de
  já ter sido visitada.
- Corrigido: um dos ramos do confronto com Rafael pulava a checagem
  automática de prazo por um turno; agora passa sempre pelo mesmo caminho.

Mudanças da v1.2 em relação à v1.1:
- Seção 20 (nova): reconstrução dos fatos, montada exclusivamente a partir
  das evidências que o jogador reuniu (E.evidencias), exibida no momento do
  indiciamento, antes da sequência de denúncia/pronúncia/veredito. Nunca usa
  a verdade objetiva do caso; pontos sem evidência ficam marcados como não
  esclarecidos. O checklist dos quatro pilares só é exibido quando o
  indiciado é Marcelo, porque foi desenhado especificamente para esse caso.

Simplificações conscientes que continuam nesta versão (documentadas para
revisão futura):
- Interceptação telefônica sempre indefere (lastro insuficiente modelado como
  sempre ausente nesta v1) — existe só para o jogador aprender o risco de
  pedir cedo demais.
- Cautelar diversa (art. 319/320) implementada de forma simplificada: uma
  escolha binária de foco (fuga x proteção), sem sub-mecânica de violação.
- Dilação de prazo: em vez do sistema categorizado de 6 pistas fixas do
  documento mestre, o tempo extra libera as diligências que ainda estejam
  disponíveis no menu normal. O teto do Final 1a após dilação continua valendo.
- Personagens de textura (Cristiane, Diego, Sérgio, Zuleide, Junior) ainda
  não têm cena própria nesta versão.
"""

import sys

# ---------------------------------------------------------------------------
# ESTADO DO JOGO
# ---------------------------------------------------------------------------

class Estado:
    def __init__(self):
        self.dia = 0                     # contador de dias corridos (sempre soma)
        self.preso = None                # None | 'marcelo' | 'rafael' | 'camila'
        self.tipo_prisao = None          # None | 'temporaria' | 'preventiva'
        self.dia_prisao = None           # dia em que a prisão foi decretada
        self.relogio1_prazo = 30
        self.dilacao_usada = False
        self.indiciado = None
        self.jogo_acabou = False
        self.texto_final = ""

        # evidências coletadas (códigos)
        self.evidencias = set()

        # flags de fase / progresso narrativo
        self.cameras_predio_obtidas = False
        self.camila_visitada = False
        self.camila_pendente = False
        self.camila_descartada = False
        self.rafael_visitado = False
        self.rafael_advogado = False   # fechou caminho informal
        self.rafael_alibi = False

        # consciência dos suspeitos: 0 = nenhuma, 1 = leve, 2 = concreto
        self.consciencia = {'marcelo': 0, 'rafael': 0, 'camila': 0}
        self.dia_gatilho_concreto = {'marcelo': None, 'rafael': None, 'camila': None}
        self.cautelar_diversa = {'marcelo': None, 'rafael': None, 'camila': None}  # None|'fuga'|'protecao'

        self.amostra_biologica_marcelo = False  # pré-requisito para DNA
        self.interceptacao_tentada = False

        # avisos de prazo já emitidos nesta partida (pra não repetir toda hora)
        self.avisos_emitidos = set()


E = Estado()


# ---------------------------------------------------------------------------
# UTILITÁRIOS
# ---------------------------------------------------------------------------

def pausa():
    input("\n(Enter para continuar) ")


def imprime(texto):
    print("\n" + texto)


def escolha(titulo, opcoes):
    """opcoes: lista de strings. Retorna o índice (1-based) escolhido.
    A opção 0 (ver resumo) é tratada automaticamente e não conta como escolha."""
    while True:
        print("\n" + "=" * 70)
        print(titulo)
        print("=" * 70)
        print("0. Ver resumo do caso")
        for i, o in enumerate(opcoes, start=1):
            print(f"{i}. {o}")
        raw = input("\n> Escolha o número: ").strip()
        if not raw.isdigit():
            print("Digite apenas o número da opção.")
            continue
        n = int(raw)
        if n == 0:
            mostrar_resumo()
            continue
        if 1 <= n <= len(opcoes):
            return n
        print("Opção inválida.")


def escolha_agrupada(titulo, grupos):
    """grupos: lista de (rotulo_da_secao, [strings de opção]).
    Numeração contínua entre grupos; a opção 0 continua mostrando o resumo.
    Retorna o índice contínuo (1-based) escolhido, para o chamador mapear
    de volta à ação correspondente."""
    total = sum(len(opcoes) for _, opcoes in grupos)
    while True:
        print("\n" + "=" * 70)
        print(titulo)
        print("=" * 70)
        print("0. Ver resumo do caso")
        contador = 1
        for rotulo, opcoes in grupos:
            if not opcoes:
                continue
            print(f"\n-- {rotulo} --")
            for o in opcoes:
                print(f"{contador}. {o}")
                contador += 1
        raw = input("\n> Escolha o número: ").strip()
        if not raw.isdigit():
            print("Digite apenas o número da opção.")
            continue
        n = int(raw)
        if n == 0:
            mostrar_resumo()
            continue
        if 1 <= n <= total:
            return n
        print("Opção inválida.")


def gastar_dias(qtd):
    E.dia += qtd


def flex(suspeito, masc, fem):
    """Concordância de gênero: Camila é a única suspeita do sexo feminino."""
    return fem if suspeito == 'camila' else masc


def dias_restantes_relogio1():
    limite = E.relogio1_prazo
    return limite - E.dia


def dias_desde_prisao():
    if E.dia_prisao is None:
        return 0
    return E.dia - E.dia_prisao


# ---------------------------------------------------------------------------
# RESUMO DO CASO (opção 0, sempre disponível)
# ---------------------------------------------------------------------------

NOME_EVIDENCIA = {
    'porteiro': "Testemunho do porteiro Antônio",
    'cameras_predio': "Câmeras do prédio (entrada 21h37 / elevador desce 22h16)",
    'camera_waldir': "Câmera externa da farmácia do Seu Waldir (carro de Marcelo saindo às 22h19)",
    'ligacao_2121': "Registro da ligação de Marcelo às 21h21 (47s)",
    'sigilo_telefonico_marcelo': "Quebra de sigilo telefônico de Marcelo (registro de chamadas)",
    'localizacao_marcelo': "Localização do celular de Marcelo próxima ao prédio",
    'sigilo_dados_helena': "Mensagens da nuvem de Helena (medida protetiva) + último ping de localização dela",
    'beatriz': "Depoimento de Beatriz Lemos (medo de Marcelo, medida protetiva)",
    'digital_parcial': "Impressão digital parcial na taça (fraca/contestável)",
    'sangue_dna': "Comparação de DNA do sangue na taça (bate com Marcelo)",
    'fechadura_laudo': "Laudo da fechadura de trinco automático (explica porta trancada)",
    'rafael_mentira': "Inconsistência de 12 min no horário que Rafael afirmou ter chegado",
    'rafael_alibi': "Álibi objetivo de Rafael (extrato de cartão do motel)",
    'camila_alibi': "Álibi confirmado de Camila (nota fiscal + 3 testemunhas)",
    'confronto_marcelo': "Confronto direto com Marcelo (admite presença, nega agressão)",
}


# ---------------------------------------------------------------------------
# SEÇÃO 20 (nova) — RECONSTRUÇÃO DOS FATOS BASEADA NO CONHECIMENTO DO JOGADOR
# ---------------------------------------------------------------------------
# Cada evidência que o jogador pode reunir (mesmos códigos de E.evidencias)
# é mapeada para um fragmento narrativo e um "balde" temporal. A reconstrução
# NUNCA usa a verdade objetiva do caso (Seção 0 do documento mestre) — usa
# exclusivamente o texto que o próprio jogo já revelou ao jogador no momento
# em que aquela evidência foi obtida. Se um código não está em E.evidencias,
# o fragmento correspondente simplesmente não aparece; nada é preenchido por
# suposição.

FRAGMENTOS_RECONSTRUCAO = {
    'beatriz': (
        'antes',
        "Segundo Beatriz Lemos, amiga próxima de Helena, ela andava com medo de "
        "Marcelo nas últimas semanas e dizia estar 'guardando print de tudo' "
        "para pedir uma medida protetiva."
    ),
    'sigilo_dados_helena': (
        'noite',
        "As mensagens recuperadas da nuvem de Helena mostram que ela vinha "
        "reunindo provas para uma medida protetiva contra Marcelo; o último "
        "ping de localização do celular dela, antes de ficar offline, foi "
        "perto do prédio, no horário do crime."
    ),
    'ligacao_2121': (
        'noite',
        "O registro telefônico confirma uma ligação de Marcelo para Helena às "
        "21h21, com duração de 47 segundos."
    ),
    'porteiro': (
        'noite',
        "O porteiro Antônio viu um homem de cerca de 1,80m, boné, entrar no "
        "prédio por volta das 21h30 — não reconheceu o rosto com clareza."
    ),
    'cameras_predio': (
        'noite',
        "As câmeras do prédio registram uma entrada às 21h37 e um elevador "
        "descendo às 22h16 — sem definição suficiente para identificar o "
        "rosto; a câmera do saguão/rua estava com defeito naquela noite."
    ),
    'camera_waldir': (
        'noite',
        "A câmera da farmácia em frente ao prédio (Seu Waldir) mostra um carro "
        "compatível com o de Marcelo Nogueira saindo da rua às 22h19."
    ),
    'fechadura_laudo': (
        'noite',
        "O laudo pericial confirma que a fechadura do apartamento é de trinco "
        "automático (mola) — tranca sozinha ao fechar, o que explica a porta "
        "encontrada trancada sem sinal de arrombamento, mesmo sem chave."
    ),
    'rafael_mentira': (
        'depois',
        "Ao ser questionado, Rafael afirmou ter chegado ao prédio por volta "
        "das 23h06 — mas o registro da portaria mostra entrada às 23h18, uma "
        "diferença de 12 minutos que ele mesmo criou."
    ),
    'rafael_alibi': (
        'depois',
        "Um extrato de cartão de crédito confirma que Rafael estava em um "
        "motel do outro lado da cidade no horário do crime."
    ),
    'camila_alibi': (
        'depois',
        "Nota fiscal e o depoimento de três testemunhas confirmam que Camila "
        "estava em um jantar de negócios em outro bairro até às 23h05."
    ),
    'digital_parcial': (
        'depois',
        "Uma impressão digital parcial na taça pode corresponder a Marcelo, "
        "mas é compatível com uma visita de quando ainda namoravam — elemento "
        "estruturalmente fraco isoladamente."
    ),
    'sangue_dna': (
        'depois',
        "O laudo de comparação de DNA confirma que o sangue encontrado na "
        "taça corresponde ao de Marcelo."
    ),
    'confronto_marcelo': (
        'depois',
        "Confrontado diretamente, Marcelo admitiu ter ido ao apartamento "
        "naquela noite 'só para conversar', mas negou qualquer agressão."
    ),
}

TITULOS_BALDE = {
    'antes': "ANTES DA NOITE DO CRIME",
    'noite': "NA NOITE DO CRIME",
    'depois': "DEPOIS — INVESTIGAÇÃO E PERÍCIA",
}


def construir_reconstrucao():
    """Monta os fragmentos narrativos correspondentes exclusivamente às
    evidências que o jogador reuniu (E.evidencias). Não usa nem consulta a
    verdade objetiva do caso em nenhum momento."""
    baldes = {'antes': [], 'noite': [], 'depois': []}
    for cod in E.evidencias:
        info = FRAGMENTOS_RECONSTRUCAO.get(cod)
        if info:
            balde, texto = info
            baldes[balde].append(texto)
    return baldes


def mostrar_reconstrucao(suspeito):
    """Seção 20: reconstrução dos fatos apresentada no momento do
    indiciamento, montada exclusivamente com o que o jogador descobriu.
    Nunca revela fatos não investigados; pontos sem evidência ficam
    marcados como não esclarecidos, nunca preenchidos por suposição."""
    baldes = construir_reconstrucao()
    total = sum(len(v) for v in baldes.values())

    print("\n" + "=" * 70)
    print("RECONSTRUÇÃO DOS FATOS — A VERSÃO QUE A SUA INVESTIGAÇÃO SUSTENTA")
    print("=" * 70)
    imprime(
        "Antes de seguir ao Ministério Público, veja como os elementos que "
        "VOCÊ reuniu se encaixam. Esta reconstrução usa exclusivamente o que "
        "a sua investigação levantou até aqui — não é a verdade absoluta do "
        "caso, é a versão que os autos, do jeito que você os montou, "
        "conseguem sustentar."
    )

    if total == 0:
        imprime(
            "Você formalizou o indiciamento sem ter reunido nenhum elemento "
            "probatório. Não há, portanto, nenhuma reconstrução a apresentar "
            "— apenas a decisão em si, sem lastro."
        )
    else:
        for chave in ('antes', 'noite', 'depois'):
            if baldes[chave]:
                imprime(TITULOS_BALDE[chave] + ":")
                for texto in baldes[chave]:
                    print(f"  • {texto}")

    if suspeito == 'marcelo':
        pendentes = []
        if not pilar1():
            pendentes.append("presença/oportunidade no local, na hora do crime")
        if not pilar2():
            pendentes.append("um vínculo ou motivo que ligue Marcelo à vítima")
        if not pilar3():
            pendentes.append("uma conexão material sólida com a cena do crime")
        if not pilar4():
            pendentes.append("uma explicação fechada para a cronologia dos fatos")
        if not elemento_genero():
            pendentes.append("prova específica do elemento de gênero (art. 121-A, §1º, CP)")

        if pendentes:
            imprime("PONTOS QUE PERMANECEM SEM ESCLARECIMENTO NOS ELEMENTOS REUNIDOS:")
            for p in pendentes:
                print(f"  • {p[0].upper()}{p[1:]}")
        else:
            imprime(
                "Os quatro pontos estruturais de uma acusação de homicídio "
                "(presença, vínculo, conexão material e cronologia) e o "
                "elemento de gênero estão, todos, sustentados por elementos "
                "que você reuniu."
            )
    else:
        imprime(
            f"Esta reconstrução reflete apenas o que a investigação levantou "
            f"sobre {suspeito.capitalize()} — o checklist de quatro pilares "
            "estruturais foi desenhado especificamente para o caso contra "
            "Marcelo Nogueira e não se aplica aqui."
        )

    print("-" * 70)
    pausa()


MINI_AULAS = {
    'sigilo_telefonico': (
        "Delegado Cordeiro",
        "Sigilo telefônico pega o registro de quem ligou pra quem e quando — não "
        "escuta o conteúdo da conversa. Serve para reconstruir contatos perto da "
        "hora do crime. Se a juíza deferir, você ganha esse histórico; se indeferir, "
        "o pedido consome tempo do inquérito mesmo assim."
    ),
    'amostra_biologica': (
        "Delegado Cordeiro",
        "Amostra biológica compulsória permite coletar material genético do "
        "suspeito para comparar com o que foi achado na cena. É o que abre a porta "
        "para a comparação de DNA. Sem lastro mínimo de presença, tende a ser "
        "indeferida."
    ),
    'dna': (
        "Dra. Fernanda Melo",
        "Comparação de DNA cruza o material genético da cena com o do suspeito. "
        "Demora mais que uma digital, mas o resultado é praticamente incontestável "
        "quando bate."
    ),
    'digital': (
        "Dra. Fernanda Melo",
        "Impressão digital compara marcas deixadas por dedos. O laudo sai rápido, "
        "mas uma digital parcial ou antiga pode ser contestada com facilidade — "
        "sozinha, raramente fecha uma tese por si só."
    ),
    'sigilo_dados': (
        "Delegado Cordeiro",
        "Sigilo de dados/nuvem acessa mensagens e arquivos guardados em backup — "
        "não é a mesma coisa que sigilo telefônico. Pode trazer conteúdo relevante "
        "sobre a vítima ou o suspeito, mas o processo costuma ser mais lento."
    ),
    'interceptacao': (
        "Delegado Cordeiro",
        "Interceptação telefônica escuta as ligações em tempo real — exige muito "
        "mais justificativa do que uma simples quebra de sigilo. Pedir sem lastro "
        "robusto tende a ser indeferido."
    ),
    'tipo_prisao': (
        "Delegado Cordeiro",
        "Temporária é pra quando ainda falta diligência rodando — dura até 10 dias, "
        "com uma prorrogação no meio do caminho. Ela não serve pra prender e "
        "esperar sentado. Preventiva não tem prazo próprio, mas ativa o prazo "
        "improrrogável de 10 dias do inquérito a partir de agora."
    ),
    'cautelar_diversa': (
        "Promotor Otávio Ramos",
        "Cautelar diversa (art. 319/320, CPP) é uma alternativa à prisão. O art. "
        "320 mira impedir fuga (retenção de passaporte, alerta de fronteira). O "
        "art. 319 mira proteção de vítima e testemunhas (proibição de aproximação, "
        "monitoramento). Cada foco resolve um problema diferente — não os dois ao "
        "mesmo tempo."
    ),
}


def mini_aula(chave, pergunta="Confirmar o pedido?"):
    """Seção 17: conversa curta com a autoridade responsável antes de confirmar uma
    medida jurídica. O conteúdo nunca muda com o estado do caso (regra de coerência
    da Seção 17: é sempre a mesma explicação institucional)."""
    autoridade, texto = MINI_AULAS[chave]
    imprime(f'{autoridade}: "{texto}"')
    op = escolha(pergunta, ["Sim, seguir com o pedido.", "Não, cancelar."])
    return op == 1


def mostrar_aula(chave):
    """Variante sem cancelamento — usada quando a decisão em si (ex.: qual tipo de
    prisão) já vem logo em seguida, sem precisar de uma confirmação separada."""
    autoridade, texto = MINI_AULAS[chave]
    imprime(f'{autoridade}: "{texto}"')
    pausa()


def pilar1():
    return ('cameras_predio' in E.evidencias and 'porteiro' in E.evidencias) \
        or ('camera_waldir' in E.evidencias) \
        or E.consciencia['marcelo'] == 2 and 'confronto_marcelo' in E.evidencias


def pilar2():
    return ('beatriz' in E.evidencias) or ('sigilo_dados_helena' in E.evidencias) \
        or ('ligacao_2121' in E.evidencias)


def pilar3():
    if 'sangue_dna' in E.evidencias:
        return True
    if 'digital_parcial' in E.evidencias and 'sigilo_dados_helena' in E.evidencias:
        return True
    return False


def pilar4():
    return ('camera_waldir' in E.evidencias) or ('fechadura_laudo' in E.evidencias) \
        or ('sangue_dna' in E.evidencias)


def elemento_genero():
    """Elemento de gênero do art. 121-A, §1º (distinto da autoria em si)."""
    return ('beatriz' in E.evidencias) or ('sigilo_dados_helena' in E.evidencias)


def mostrar_resumo():
    print("\n" + "-" * 70)
    print("RESUMO DO CASO — CASO 001: O Apartamento 804")
    print("-" * 70)
    if E.preso:
        print(f"Situação: {E.preso.capitalize()} está PRESO ({E.tipo_prisao}).")
        print(f"Relógio 2 (10 dias improrrogáveis): dia {dias_desde_prisao()} de 10.")
    else:
        print(f"Relógio 1 (fase solto): dia {E.dia} de {E.relogio1_prazo}"
              f"{' (dilação já usada)' if E.dilacao_usada else ''}.")

    print("\nPilares estruturais do caso contra Marcelo:")
    print(f"  1. Presença/oportunidade .... {'FECHADO' if pilar1() else 'em aberto'}")
    print(f"  2. Vínculo com a vítima ..... {'FECHADO' if pilar2() else 'em aberto'}")
    print(f"  3. Conexão material ......... {'FECHADO' if pilar3() else 'em aberto'}")
    print(f"  4. Fecha a cronologia ....... {'FECHADO' if pilar4() else 'em aberto'}")
    print(f"  Elemento de gênero (art. 121-A, §1º): {'demonstrado' if elemento_genero() else 'ainda não demonstrado'}")

    print("\nProvas e informações reunidas:")
    if not E.evidencias:
        print("  (nenhuma ainda)")
    for cod in E.evidencias:
        print(f"  - {NOME_EVIDENCIA.get(cod, cod)}")

    print("\nSuspeitos:")
    for s in ('marcelo', 'rafael', 'camila'):
        nivel = {0: 'nenhuma', 1: 'leve (foi ouvido)', 2: 'CONCRETA (sabe que é alvo direto)'}[E.consciencia[s]]
        extra = ""
        if E.consciencia[s] == 2 and E.preso != s:
            dias_desde = E.dia - E.dia_gatilho_concreto[s]
            limite = 10 if E.cautelar_diversa[s] == 'fuga' else 5
            extra = f"  [relógio de consciência: {dias_desde}/{limite} dias]"
        print(f"  - {s.capitalize()}: consciência {nivel}{extra}")
    if E.camila_descartada:
        print("  (Camila já foi descartada da investigação)")
    if E.rafael_alibi:
        print("  (Rafael já tem álibi objetivo confirmado)")

    print("-" * 70)


def linha_status_tempo():
    """Uma linha curta e sempre visível com o estado dos relógios ativos —
    para o jogador nunca precisar abrir o resumo (opção 0) só para saber
    quanto tempo resta."""
    partes = []
    if E.preso:
        partes.append(f"Prisão de {E.preso.capitalize()}: dia {dias_desde_prisao()} de 10")
    else:
        partes.append(f"Inquérito: dia {E.dia} de {E.relogio1_prazo}")

    for s in ('marcelo', 'rafael', 'camila'):
        if E.consciencia[s] == 2 and E.preso != s and E.dia_gatilho_concreto[s] is not None:
            limite = 10 if E.cautelar_diversa[s] == 'fuga' else 5
            restam = limite - (E.dia - E.dia_gatilho_concreto[s])
            partes.append(f"{s.capitalize()} sabe que é alvo: {max(restam, 0)} dia(s) até risco de fuga")

    return " | ".join(partes)


def avisar_prazos_criticos():
    """Emite um alerta explícito (uma vez só por limiar) quando um relógio
    está prestes a esgotar, em vez de deixar o jogador descobrir tarde
    demais."""
    if not E.preso and E.indiciado is None:
        restam = E.relogio1_prazo - E.dia
        chave = f"relogio1_{E.relogio1_prazo}_baixo"
        if restam <= 3 and chave not in E.avisos_emitidos:
            E.avisos_emitidos.add(chave)
            imprime(
                f"[AVISO DE PRAZO] Faltam {restam} dia(s) para o limite de "
                f"{E.relogio1_prazo} dias do inquérito. Se o prazo estourar sem "
                "indiciamento, você vai precisar decidir na hora entre indiciar "
                "com o que tem ou pedir dilação."
            )
            pausa()

    if E.preso and E.indiciado is None:
        restam = 10 - dias_desde_prisao()
        chave = f"relogio2_preso_{E.preso}_baixo"
        if restam <= 3 and chave not in E.avisos_emitidos:
            E.avisos_emitidos.add(chave)
            imprime(
                f"[AVISO DE PRAZO] Faltam {restam} dia(s) para o limite "
                f"improrrogável de 10 dias com {E.preso.capitalize()} preso. Se "
                "estourar sem denúncia, a prisão pode ser relaxada."
            )
            pausa()

    for s in ('marcelo', 'rafael', 'camila'):
        if E.consciencia[s] == 2 and E.preso != s and E.dia_gatilho_concreto[s] is not None:
            limite = 10 if E.cautelar_diversa[s] == 'fuga' else 5
            restam = limite - (E.dia - E.dia_gatilho_concreto[s])
            chave = f"fuga_{s}_baixo"
            if restam <= 2 and chave not in E.avisos_emitidos:
                E.avisos_emitidos.add(chave)
                imprime(
                    f"[AVISO DE PRAZO] {s.capitalize()} sabe que é alvo da "
                    f"investigação e o risco de fuga aumenta a cada dia. Restam "
                    f"{max(restam, 0)} dia(s) antes que isso possa fugir do seu controle."
                )
                pausa()


# ---------------------------------------------------------------------------
# VERIFICAÇÃO DE FIM DE JOGO (fuga, prazo, prisão estourada)
# ---------------------------------------------------------------------------

def checar_condicoes_automaticas():
    """Chamado depois de qualquer ação que gasta dias. Pode terminar o jogo."""
    if E.jogo_acabou:
        return

    avisar_prazos_criticos()
    if E.jogo_acabou:
        return

    # Índice de fuga
    for s in ('marcelo', 'rafael', 'camila'):
        if E.consciencia[s] == 2 and E.preso != s and E.dia_gatilho_concreto[s] is not None:
            limite = 10 if E.cautelar_diversa[s] == 'fuga' else 5
            if E.dia - E.dia_gatilho_concreto[s] >= limite:
                if s == 'marcelo':
                    final_6()
                    return
                else:
                    # Rafael/Camila não fogem; só param de cooperar informalmente,
                    # se ainda não tiverem parado.
                    if s == 'rafael':
                        E.rafael_advogado = True

    # Prazo do Relógio 2 (preso, 10 dias improrrogáveis)
    if E.preso and E.indiciado is None:
        if dias_desde_prisao() > 10:
            cena_relaxamento()
            return

    # Prazo do Relógio 1 (solto, 30 dias, prorrogável 1x)
    if not E.preso and E.indiciado is None and E.dia >= E.relogio1_prazo:
        cena_dilacao()
        return


# ---------------------------------------------------------------------------
# FINAIS
# ---------------------------------------------------------------------------

def finalizar(titulo, texto):
    E.jogo_acabou = True
    print("\n" + "#" * 70)
    print(titulo)
    print("#" * 70)
    print(texto)
    mostrar_resumo()


def final_6():
    finalizar(
        "FINAL 6 — MARCELO FOGE",
        "Você chega para prendê-lo, ou para formalizar a denúncia, e a casa está "
        "vazia. Um vizinho diz que um carro de mudança passou dois dias antes. "
        "O advogado dele, Dr. Henrique Salles, informa que não sabe do "
        "paradeiro do cliente.\n\n"
        + ("Se os quatro pilares já estivessem fechados contra ele, a prova "
           "existia — só faltou agir a tempo, depois que ele já sabia que era o alvo.\n"
           if pilar1() and pilar2() and pilar3() and pilar4() else
           "O caso, de qualquer forma, ainda não estava fechado contra ele — "
           "faltavam elementos, e agora também falta o próprio Marcelo.\n")
    )


def cena_relaxamento():
    imprime(
        "O prazo de 10 dias improrrogáveis (art. 10, CPP) com o suspeito preso "
        "se esgotou sem que você formalizasse a denúncia. A juíza Marília Costa "
        "precisa decidir o que fazer com a custódia."
    )
    op = escolha(
        "O que fazer?",
        [
            "Aceitar o relaxamento puro da prisão — ele fica solto, sem nenhuma cautelar.",
            "Pedir a conversão em cautelar diversa (art. 319/320, CPP) — ele fica solto, mas monitorado.",
        ],
    )
    suspeito = E.preso
    if op == 1:
        E.preso = None
        E.dia_prisao = None
        finalizar(
            "FINAL 5a — PRISÃO RELAXADA POR EXCESSO DE PRAZO",
            f"{suspeito.capitalize()} é solto sem nenhuma restrição. Pior cenário "
            "possível mesmo que ele fosse mesmo o culpado certo — o inquérito "
            "não conseguiu se fechar a tempo dentro do prazo rígido da prisão."
        )
    else:
        gastar_dias(1)
        E.preso = None
        E.dia_prisao = None
        E.cautelar_diversa[suspeito] = 'fuga'
        E.dia_gatilho_concreto[suspeito] = E.dia
        finalizar(
            "FINAL 5b — CONVERSÃO EM CAUTELAR DIVERSA",
            f"{suspeito.capitalize()} fica solto, mas monitorado (retenção de "
            "passaporte, alerta de fronteira). Cenário intermediário: nem a "
            "prisão nem o relaxamento puro — a investigação ainda pode continuar, "
            "mas o tempo já apertou bastante."
        )


def cena_dilacao():
    imprime(
        "Chegou o último dia do prazo de 30 dias do inquérito (art. 10, CPP, "
        "fase solto), e você ainda não formalizou nenhum indiciamento. O "
        "Delegado Cordeiro pede sua decisão."
    )
    if E.dilacao_usada:
        # já usou dilação uma vez, não há nova prorrogação
        indiciar_com_o_que_ha(forcado=True)
        return
    op = escolha(
        "O que fazer?",
        [
            "Indiciar agora, com os elementos que você já tem.",
            "Pedir dilação de prazo ao juiz (só pode ser concedida uma vez por partida).",
        ],
    )
    if op == 1:
        indiciar_com_o_que_ha(forcado=True)
    else:
        E.relogio1_prazo += 10
        E.dilacao_usada = True
        imprime(
            "A juíza concede mais 10 dias — mas o Promotor Otávio Ramos avisa: "
            "mesmo que você feche a autoria agora, o tempo extra não é suficiente "
            "para também sustentar o contexto de violência de gênero dentro do "
            "prazo estendido. O teto máximo, a partir de agora, é homicídio simples."
        )
        pausa()


def indiciar_com_o_que_ha(forcado=False):
    """Usado tanto pela ação voluntária do jogador quanto pelo estouro de prazo."""
    if E.jogo_acabou:
        return
    if forcado and E.indiciado is None and not E.preso and E.dia >= E.relogio1_prazo:
        # Verifica se há alguém plausível para indiciar; se ninguém foi
        # sequer investigado com alguma suspeita, é Final 4 puro.
        if not E.evidencias:
            finalizar(
                "FINAL 4 — PRAZO ESGOTADO SEM ACUSAÇÃO",
                "O inquérito é encaminhado sem indiciamento formal. Nenhuma prisão, "
                "nenhuma acusação. O tempo passou e nada foi formalizado."
            )
            return
    op = escolha(
        "Contra quem você formaliza o indiciamento?",
        ["Marcelo Nogueira", "Rafael Duarte", "Camila Torres", "Ninguém — encerrar sem indiciar"],
    )
    if op == 4:
        finalizar(
            "FINAL 4 — PRAZO ESGOTADO SEM ACUSAÇÃO",
            "O inquérito é encaminhado sem indiciamento formal. Nenhuma prisão, "
            "nenhuma acusação. Se você tinha os quatro pilares fechados contra "
            "alguém, a prova existia — só faltou a decisão de agir dentro do prazo."
            if pilar1() and pilar2() and pilar3() and pilar4() else
            "O inquérito é encaminhado sem indiciamento formal. Nenhuma prisão, "
            "nenhuma acusação."
        )
        return
    suspeito = ['marcelo', 'rafael', 'camila'][op - 1]
    E.indiciado = suspeito
    mostrar_reconstrucao(suspeito)
    sequencia_final(suspeito)


# ---------------------------------------------------------------------------
# SEÇÃO 18 — SEQUÊNCIA FINAL: DENÚNCIA → PRONÚNCIA → VEREDITO
# ---------------------------------------------------------------------------

def sequencia_final(suspeito):
    if suspeito == 'rafael' and E.rafael_alibi:
        imprime(
            "Você formaliza o indiciamento contra Rafael — mas o próprio "
            "extrato de cartão que sua investigação já reuniu mostra que ele "
            "estava em outro lugar na hora do crime. O Promotor Otávio Ramos "
            "recusa a denúncia: 'Não posso denunciar alguém que os próprios "
            "autos já inocentam.'"
        )
        finalizar(
            "INDICIAMENTO REJEITADO PELO MP",
            "O caso volta para a investigação. Rafael está formalmente fora. "
            "Continue investigando (rode o jogo novamente para explorar outro caminho, "
            "ou — nesta v1 — considere isso o fim da partida)."
        )
        return

    if suspeito == 'camila' and E.camila_descartada:
        imprime(
            "Você formaliza o indiciamento contra Camila — mas a nota fiscal e "
            "as três testemunhas do jantar já provam que ela estava em outro "
            "bairro. O Promotor recusa a denúncia."
        )
        finalizar(
            "INDICIAMENTO REJEITADO PELO MP",
            "O caso volta para a investigação. Camila está formalmente fora."
        )
        return

    imprime(
        f"O inquérito é encerrado e encaminhado ao Ministério Público, com "
        f"{suspeito.capitalize()} indiciado."
    )
    pausa()

    if suspeito in ('rafael', 'camila'):
        finalizar(
            "FINAL 3 — CONDENAÇÃO DE INOCENTE",
            f"O Promotor Otávio Ramos denuncia, a Juíza Marília Costa pronuncia, "
            f"e o júri condena {suspeito.capitalize()} — que é inocente. "
            "Os sinais (motivo, acesso, comportamento evasivo) pareciam fortes o "
            "suficiente, mas nenhuma prova material realmente ligava essa pessoa "
            "ao crime. O verdadeiro responsável nunca foi alcançado."
        )
        return

    # Suspeito == marcelo
    p1, p2, p3, p4 = pilar1(), pilar2(), pilar3(), pilar4()
    autoria_completa = p1 and p2 and p3 and p4

    if not autoria_completa:
        finalizar(
            "FINAL 2 — ABSOLVIDO POR INSUFICIÊNCIA PROBATÓRIA",
            "Marcelo é mesmo o culpado — mas o caso que chegou ao júri tinha "
            "buracos: "
            + ("" if p1 else "faltou fechar presença/oportunidade. ")
            + ("" if p2 else "faltou fechar o vínculo com a vítima. ")
            + ("" if p3 else "faltou uma conexão material sólida com a cena. ")
            + ("" if p4 else "faltou fechar a cronologia dos fatos. ")
            + "\n\nVocê 'sentiu' certo, mas não construiu o caso. Marcelo é absolvido."
        )
        return

    # Ponto 1 — Denúncia (Promotor Otávio Ramos)
    imprime(
        "PONTO 1 — DENÚNCIA (Promotor Otávio Ramos)\n\n"
        "O Promotor Otávio Ramos examina os autos. A autoria do homicídio está "
        "bem demonstrada. Ele olha então, separadamente, para o que existe sobre "
        "o motivo — e mais especificamente sobre se há prova de que Marcelo agiu "
        "por razões da condição do sexo feminino (art. 121-A, §1º, CP: violência "
        "doméstica/familiar, ou menosprezo/discriminação)."
    )
    tem_genero_denuncia = elemento_genero() and not E.dilacao_usada
    if tem_genero_denuncia:
        imprime(
            "'Temos o depoimento de Beatriz Lemos e/ou as mensagens da medida "
            "protetiva que Helena estava reunindo. Isso é elemento de gênero "
            "suficiente. Vou denunciar por feminicídio, art. 121-A do Código Penal.'"
        )
        capitulacao_denuncia = 'feminicidio'
    else:
        motivo = "o prazo estourou e precisamos ir com o que temos" if E.dilacao_usada else \
                 "não há prova específica do elemento de gênero nos autos"
        imprime(
            f"'A autoria está sólida, mas {motivo}. Vou denunciar por homicídio "
            "simples, art. 121, caput, do Código Penal — não vou arriscar uma "
            "capitulação que não sustento com prova.'"
        )
        capitulacao_denuncia = 'homicidio_simples'
    pausa()

    # Ponto 2 — Pronúncia (Juíza Marília Costa)
    imprime(
        "PONTO 2 — PRONÚNCIA (Juíza Marília Costa)\n\n"
        "Antes de mandar o caso a júri, a juíza Marília Costa reexamina os "
        "autos, olhando de novo para os mesmos dois pontos: autoria e elemento "
        "de gênero."
    )
    capitulacao_final = capitulacao_denuncia
    if capitulacao_denuncia == 'feminicidio' and not elemento_genero():
        # (não deveria acontecer dado o cálculo acima, mas mantido por robustez)
        capitulacao_final = 'homicidio_simples'
    if capitulacao_denuncia == 'feminicidio':
        imprime(
            "'Os elementos de gênero seguem presentes e consistentes. Mantenho "
            "a pronúncia por feminicídio, art. 121-A. O caso vai a júri assim.'"
        )
    else:
        imprime(
            "'Confirmo a capitulação da denúncia — não há, nos autos, prova "
            "suficiente do elemento de gênero. O caso vai a júri por homicídio "
            "simples, art. 121, caput.'"
        )
    pausa()

    # Ponto 3 — Plenário/veredito
    imprime(
        "PONTO 3 — PLENÁRIO E VEREDITO\n\n"
        "O Tribunal do Júri se reúne. A autoria está bem demonstrada nos autos "
        "e o Conselho de Sentença condena Marcelo Nogueira, na capitulação que "
        "chegou até aqui."
    )

    if capitulacao_final == 'feminicidio':
        finalizar(
            "FINAL 1a — CONDENAÇÃO POR FEMINICÍDIO (art. 121-A, CP — Lei 14.994/2024)",
            "Marcelo Nogueira é condenado por feminicídio: reclusão de 20 a 40 "
            "anos, crime hediondo. A reconstrução dos fatos bate exatamente com "
            "o que realmente aconteceu no apartamento 804 — autoria demonstrada "
            "e o contexto de violência de gênero comprovado, sem atalhos."
        )
    else:
        finalizar(
            "FINAL 1b — CONDENAÇÃO POR HOMICÍDIO SIMPLES (art. 121, caput, CP)",
            "Marcelo Nogueira é condenado por homicídio, mas sem o tipo penal "
            "do art. 121-A — pena menor, sem a classificação como feminicídio. "
            "A autoria está certa, mas o elemento de gênero não foi (ou não pôde "
            "mais ser) demonstrado a tempo."
        )


# ---------------------------------------------------------------------------
# AÇÕES — CENA 1 e CENA 2 (abertura guiada)
# ---------------------------------------------------------------------------

def abertura():
    imprime(
        "Você é chamado ainda de madrugada. Um corpo foi encontrado no "
        "apartamento 804 de um prédio residencial de médio padrão. A vítima: "
        "Helena Duarte, 34 anos. O porteiro do prédio, Antônio, está sentado "
        "no saguão, visivelmente abalado, esperando alguém para falar.\n\n"
        "Você sobe até o 804. A porta estava trancada quando os primeiros "
        "policiais chegaram, sem sinal de arrombamento. Dentro, a cena: uma "
        "taça quebrada perto do corpo, uma mancha de sangue que não parece "
        "ser só da vítima."
    )
    imprime(
        "O celular da vítima está caído perto do corpo, tela quebrada, mas "
        "ainda ligado — dá pra ver a última chamada recebida às 21h21 e, na "
        "tela de bloqueio, uma notificação de mensagem de \"Rafael (irmão)\": "
        "\"me liga assim que puder, preciso te contar uma coisa\". Um dos "
        "policiais que chegou primeiro já está cutucando o corpo pra virar "
        "o rosto da vítima. Você tem que decidir agora o que priorizar."
    )
    pausa()
    op = escolha(
        "CENA 1 — A primeira decisão",
        [
            "Priorizar preservar a cena e colher evidências físicas antes de qualquer coisa.",
            "Ligar agora mesmo para o irmão de Helena, Rafael, e já tentar falar com ele.",
        ],
    )
    if op == 1:
        gastar_dias(1)
        imprime(
            "Você manda o policial parar de mexer no corpo e isola o "
            "apartamento antes de mais nada. A perícia chega com a cena "
            "intacta — o que vai ajudar qualquer prova física que você for "
            "buscar mais tarde. A mensagem de Rafael no celular da vítima "
            "vai ter que esperar."
        )
    else:
        gastar_dias(1)
        E.rafael_visitado = True
        E.consciencia['rafael'] = max(E.consciencia['rafael'], 1)
        imprime(
            "Rafael atende, a voz embargada. Ele confirma que é irmão de "
            "Helena e diz que vai até a delegacia assim que puder. Você ganha "
            "uma primeira impressão dele — abalado, mas nervoso de um jeito "
            "que você ainda não sabe explicar. Enquanto isso, sem ninguém "
            "coordenando a cena, o policial que estava mexendo no corpo "
            "continua mexendo: quando a perícia finalmente chega, registra "
            "que a posição original do corpo já não pode ser confirmada com "
            "certeza."
        )
    pausa()

    op = escolha(
        "CENA 2 — Antônio, o porteiro, ainda está lá embaixo",
        [
            "Interrogar Antônio agora, sobre o que ele viu essa noite.",
            "Pedir as imagens das câmeras do prédio primeiro.",
        ],
    )
    if op == 1:
        gastar_dias(1)
        E.evidencias.add('porteiro')
        imprime(
            "Antônio conta que viu um homem, cerca de 1,80m, boné, entrar por "
            "volta das 21h30. Não reconheceu o rosto direito. Diz que ficou "
            "atendendo outra pessoa na portaria por um tempo, mais tarde, e "
            "pode ter perdido alguma saída."
        )
    else:
        gastar_dias(1)
        E.evidencias.add('cameras_predio')
        E.cameras_predio_obtidas = True
        imprime(
            "As câmeras do prédio mostram uma entrada às 21h37 e uma descida "
            "de elevador às 22h16 — mas a definição é baixa, não dá pra "
            "reconhecer o rosto com clareza. Pior: a câmera do saguão/rua, que "
            "confirmaria quem realmente saiu do prédio, estava com defeito "
            "naquela noite."
        )
    pausa()
    checar_condicoes_automaticas()


def cena_3():
    """Seção 3 do mapa: círculo da vítima, em duas decisões binárias em sequência
    (nunca uma escolha tripla). Só decide quem a história apresenta primeiro —
    os outros suspeitos continuam alcançáveis depois, pelo menu livre normal."""
    if E.jogo_acabou:
        return
    imprime(
        "Do celular recuperado e dos primeiros relatos de vizinhos e colegas, "
        "três nomes se repetem:\n\n"
        "- Rafael Duarte, irmão de Helena — a mensagem dele já apareceu na "
        "tela travada do celular, pedindo pra ela ligar de volta.\n"
        "- Camila Torres, sócia de Helena no escritório — colegas comentam "
        "que as duas tiveram uma discussão feia sobre a sociedade na semana "
        "passada.\n"
        "- Marcelo Nogueira, ex-namorado de Helena — terminaram há cerca de "
        "três semanas; uma vizinha comenta, meio sem graça, que via ele "
        "rondando o prédio de vez em quando depois disso.\n\n"
        "Você não tem recursos pra falar com os três ao mesmo tempo agora — "
        "precisa escolher por onde entrar."
    )
    op = escolha(
        "CENA 3 — Círculo da vítima",
        [
            "Focar primeiro no círculo pessoal/familiar (Rafael).",
            "Focar primeiro no círculo profissional/afetivo (Camila e Marcelo).",
        ],
    )
    if op == 1:
        acao_investigar_rafael()
    else:
        op2 = escolha(
            "Dentro do círculo profissional/afetivo, por onde começar?",
            [
                "Investigar Camila (a sócia).",
                "Focar em Marcelo (o ex-companheiro).",
            ],
        )
        if op2 == 1:
            acao_investigar_camila()
        else:
            imprime(
                "Você decide abrir a investigação com atenção especial a Marcelo "
                "Nogueira, o ex-companheiro de Helena — sem descartar os outros "
                "nomes por enquanto."
            )
            pausa()

    if E.jogo_acabou:
        return
    imprime(
        "Vasculhando as redes sociais de Helena em busca de mais contexto, um "
        "nome aparece comentando quase todas as postagens dos últimos meses: "
        "Beatriz Lemos. Uma colega do escritório confirma — as duas eram "
        "amigas próximas, quase irmãs. Se alguém sabia como Helena andava se "
        "sentindo nas últimas semanas, provavelmente é ela."
    )
    pausa()


# ---------------------------------------------------------------------------
# AÇÕES — MENU LIVRE (investigação principal)
# ---------------------------------------------------------------------------

def acao_porteiro():
    gastar_dias(1)
    E.evidencias.add('porteiro')
    imprime(
        "Antônio confirma o que já disse: um homem de cerca de 1,80m, boné, "
        "entrou por volta das 21h30. Detalhe genérico — não fecha nada sozinho, "
        "mas ajuda a bater com outras provas."
    )
    pausa()


def acao_cameras_predio():
    gastar_dias(1)
    E.evidencias.add('cameras_predio')
    E.cameras_predio_obtidas = True
    imprime(
        "As imagens confirmam entrada às 21h37 e elevador descendo às 22h16 — "
        "mas sem definição de rosto, e sem câmera de saguão/rua funcionando "
        "naquela noite."
    )
    pausa()


def acao_laudo_fechadura():
    gastar_dias(1)
    E.evidencias.add('fechadura_laudo')
    imprime(
        "A perícia confirma: a fechadura do apartamento 804 é de trinco automático "
        "(mola) — tranca sozinha ao fechar, sem precisar de chave por fora. Isso "
        "explica a porta encontrada trancada e sem sinal de arrombamento, mesmo que "
        "quem saiu por último não tivesse cópia da chave."
    )
    pausa()
    checar_condicoes_automaticas()


def acao_cameras_vizinhas():
    gastar_dias(2)
    E.evidencias.add('camera_waldir')
    imprime(
        "Você lembra que há uma farmácia bem em frente ao prédio. O dono, Seu "
        "Waldir, tem uma câmera própria voltada pra rua. Ele mostra a gravação, "
        "sem hesitar: às 22h19, um carro compatível com o de Marcelo Nogueira "
        "sai da rua. É a peça que faltava para ligar a descida do elevador a "
        "alguém realmente deixando o local."
    )
    pausa()


def _verificar_liberacao_por_inocencia(suspeito):
    """Seção 15.1: se o suspeito preso for Rafael ou Camila e a prova que o
    inocenta aparece durante a custódia, ele é solto na hora — não é preciso
    esperar o prazo de 10 dias estourar."""
    if E.preso == suspeito:
        E.preso = None
        E.dia_prisao = None
        imprime(
            f"{suspeito.capitalize()} estava preso — mas a prova que acabou de "
            "aparecer o inocenta. A juíza Marília Costa determina a soltura "
            "imediata, por comprovação de inocência. O caso contra ele se encerra "
            "aqui; a investigação sobre os demais continua."
        )
        pausa()


def acao_investigar_camila():
    if E.camila_visitada:
        imprime("Você já investigou Camila. Não há nada de novo a fazer aqui por enquanto.")
        pausa()
        return
    gastar_dias(1)
    E.camila_visitada = True
    imprime(
        "Camila Torres, sócia de Helena, recebe você no escritório. Direta: "
        "'Sim, brigamos por dinheiro. Isso é público, está registrado até em "
        "notificação extrajudicial.' Ela não parece nervosa — só incomodada "
        "com a situação."
    )
    op = escolha(
        "Como você conduz?",
        [
            "Aceitar a explicação e seguir — parece razoável.",
            "Exigir comprovação do álibi dela para aquela noite.",
        ],
    )
    if op == 1:
        E.camila_pendente = True
        imprime(
            "Você segue em frente. Camila fica como suspeita 'em aberto' — vai "
            "precisar ser descartada mais cedo ou mais tarde, o que vai custar "
            "tempo depois."
        )
    else:
        E.camila_descartada = True
        E.evidencias.add('camila_alibi')
        imprime(
            "Em poucas horas chega a nota fiscal do restaurante e a "
            "confirmação de três testemunhas — sócios de outra empresa. Camila "
            "estava em um jantar de negócios em outro bairro até às 23h05. "
            "Ela está oficialmente fora, com custo baixo de tempo."
        )
    pausa()
    _verificar_liberacao_por_inocencia('camila')
    checar_condicoes_automaticas()


def acao_investigar_rafael():
    if not E.rafael_visitado:
        E.rafael_visitado = True
        E.consciencia['rafael'] = max(E.consciencia['rafael'], 1)
    imprime(
        "Rafael Duarte, o irmão de Helena, tem a chave do apartamento. Ao ser "
        "perguntado sobre a ligação que teve com a irmã, ele hesita. Surge "
        "também uma disputa de herança entre os dois — motivo financeiro, "
        "ainda que antigo. E, quando confrontado com o horário registrado na "
        "portaria, ele erra a própria versão: afirma ter chegado por volta das "
        "23h06 — mas a portaria mostra entrada às 23h18. Doze minutos de "
        "diferença que ele mesmo criou."
    )
    E.evidencias.add('rafael_mentira')
    op = escolha(
        "Como você conduz a partir daqui?",
        [
            "Confrontar Rafael diretamente com a inconsistência de horário.",
            "Investigar discretamente onde ele estava antes de chegar (mais lento, mais seguro).",
        ],
    )
    if op == 1:
        imprime(
            "Aviso: confrontar agora é definitivo — ele vai saber que é "
            "suspeito, e isso pode mudar o comportamento dele daqui pra frente."
        )
        confirmar = escolha("Confirmar o confronto?", ["Sim, confrontar agora.", "Não, prefiro investigar discretamente."])
        if confirmar == 2:
            acao_investigar_rafael_discreto()
        else:
            gastar_dias(1)
            E.consciencia['rafael'] = 2
            E.dia_gatilho_concreto['rafael'] = E.dia
            imprime(
                "Rafael entra em pânico, gagueja, se recusa a explicar de imediato: "
                "'Isso não importa agora!' Ele parece mais suspeito do que nunca — "
                "mas isso pode ser só vergonha, não culpa."
            )
            op2 = escolha(
                "Você insiste, ali mesmo, para que ele explique agora?",
                [
                    "Insistir, pressionando pela explicação na hora.",
                    "Deixar por isso mesmo — ele vai chamar um advogado de família.",
                ],
            )
            if op2 == 1:
                gastar_dias(1)
                E.rafael_alibi = True
                E.evidencias.add('rafael_alibi')
                imprime(
                    "Sob pressão direta, ele cede: 'Isso vai ficar entre nós, mas eu "
                    "estava com uma pessoa. Vou te dar o contato dela.' Álibi "
                    "confirmado — Rafael estava em outro lugar quando o crime "
                    "aconteceu. Ele completa, sem graça: 'aquele recado que mandei "
                    "pra ela, pedindo pra ligar de volta — era sobre isso, sobre "
                    "eu não saber como contar pra família. Não tinha nada a ver "
                    "com... com o que aconteceu.'"
                )
                _verificar_liberacao_por_inocencia('rafael')
            else:
                E.rafael_advogado = True
                imprime(
                    "Rafael contrata um advogado de família. A partir de agora, o "
                    "caminho informal está fechado — só quebra de sigilo bancário/"
                    "cartão formal reabre o acesso a essa informação."
                )
    else:
        acao_investigar_rafael_discreto()
    pausa()
    checar_condicoes_automaticas()


def acao_investigar_rafael_discreto():
    if E.rafael_alibi:
        return
    gastar_dias(2)
    E.rafael_alibi = True
    E.evidencias.add('rafael_alibi')
    imprime(
        "Leva mais tempo, mas você encontra um registro de cartão de crédito "
        "em um motel do outro lado da cidade, no horário do crime. Álibi "
        "objetivo — sem precisar que Rafael confesse nada. O caso extraconjugal "
        "também explica, agora, o recado que ele tinha mandado pra Helena antes "
        "de tudo: não era sobre o crime, era sobre não saber como contar isso "
        "pra família."
    )
    _verificar_liberacao_por_inocencia('rafael')


def acao_rafael_sigilo_bancario():
    if E.rafael_alibi:
        imprime("Você já tem o álibi de Rafael confirmado. Não é necessário pedir isso de novo.")
        pausa()
        return
    gastar_dias(2)
    E.consciencia['rafael'] = max(E.consciencia['rafael'], 2)
    if E.dia_gatilho_concreto['rafael'] is None:
        E.dia_gatilho_concreto['rafael'] = E.dia
    E.rafael_alibi = True
    E.evidencias.add('rafael_alibi')
    imprime(
        "A juíza Marília Costa defere a quebra de sigilo bancário/cartão. O "
        "extrato mostra o mesmo motel do outro lado da cidade, no horário do "
        "crime. Álibi objetivo confirmado por via formal — e explica, de "
        "quebra, o recado que ele tinha mandado pra Helena antes de tudo: não "
        "tinha relação com o crime, só com o caso extraconjugal que ele estava "
        "escondendo da família."
    )
    pausa()
    _verificar_liberacao_por_inocencia('rafael')


def acao_beatriz():
    gastar_dias(1)
    E.evidencias.add('beatriz')
    imprime(
        "Beatriz Lemos, amiga próxima de Helena, conta que ela andava com medo "
        "de Marcelo nas últimas semanas — tinha comentado que estava 'guardando "
        "print de tudo' para pedir uma medida protetiva."
    )
    pausa()
    checar_condicoes_automaticas()


def _gatilhar_marcelo():
    if E.consciencia['marcelo'] < 2:
        E.consciencia['marcelo'] = 2
        E.dia_gatilho_concreto['marcelo'] = E.dia


def acao_sigilo_telefonico_marcelo():
    if not mini_aula('sigilo_telefonico'):
        return
    gastar_dias(1)
    _gatilhar_marcelo()
    if 'cameras_predio' in E.evidencias or 'ligacao_2121' in E.evidencias:
        E.evidencias.add('sigilo_telefonico_marcelo')
        E.evidencias.add('ligacao_2121')
        imprime(
            "Deferida. O registro mostra uma ligação de Marcelo para Helena às "
            "21h21, durando 47 segundos, na noite do crime. Prova contato — não "
            "prova presença dentro do apartamento."
        )
    else:
        imprime(
            "A juíza indefere: 'Os elementos apresentados não demonstram, neste "
            "momento, a necessidade da medida.' O advogado de Marcelo, Dr. "
            "Henrique Salles, já fica sabendo do pedido — mesmo indeferido."
        )
    pausa()
    checar_condicoes_automaticas()


def acao_amostra_biologica_marcelo():
    if not mini_aula('amostra_biologica'):
        return
    gastar_dias(1)
    _gatilhar_marcelo()
    if 'cameras_predio' in E.evidencias or 'camera_waldir' in E.evidencias:
        E.amostra_biologica_marcelo = True
        imprime(
            "Deferida a amostra biológica compulsória. Dr. Henrique Salles "
            "contesta formalmente, mas a coleta é feita."
        )
    else:
        imprime(
            "Indeferida — ainda não há elementos mínimos de presença para "
            "justificar a medida. O pedido, mesmo negado, já alerta o advogado "
            "de Marcelo."
        )
    pausa()
    checar_condicoes_automaticas()


def acao_comparacao_dna():
    if not E.amostra_biologica_marcelo:
        imprime(
            "Você ainda não tem uma amostra biológica de Marcelo para "
            "comparar. Peça a amostra biológica compulsória (ou voluntária) "
            "primeiro."
        )
        pausa()
        return
    if not mini_aula('dna'):
        return
    gastar_dias(3)
    E.evidencias.add('sangue_dna')
    imprime(
        "O laudo da Dra. Fernanda Melo chega: o sangue na taça bate com o DNA "
        "de Marcelo. Resultado forte, praticamente incontestável."
    )
    pausa()
    checar_condicoes_automaticas()


def acao_impressao_digital():
    if not mini_aula('digital'):
        return
    gastar_dias(1)
    E.evidencias.add('digital_parcial')
    imprime(
        "Uma impressão digital parcial na taça pode 'bater' com Marcelo — mas "
        "ele e Helena namoraram até três semanas antes, então uma digital "
        "antiga é esperada e facilmente contestável como residual de visita "
        "anterior. Resultado rápido, mas estruturalmente fraco sozinho."
    )
    pausa()
    checar_condicoes_automaticas()


def acao_sigilo_dados_helena():
    if not mini_aula('sigilo_dados'):
        return
    gastar_dias(3)
    E.evidencias.add('sigilo_dados_helena')
    imprime(
        "Deferida a quebra de sigilo de dados/nuvem da conta de Helena. Vêm "
        "junto duas coisas: mensagens em que ela reunia provas para uma medida "
        "protetiva contra Marcelo, e o último ping de localização do celular "
        "dela antes de ficar offline — perto do prédio, no horário do crime. "
        "Essa medida mira a conta de Helena, não Marcelo diretamente."
    )
    pausa()
    checar_condicoes_automaticas()


def acao_interceptacao():
    if not mini_aula('interceptacao'):
        return
    gastar_dias(1)
    _gatilhar_marcelo()
    E.interceptacao_tentada = True
    imprime(
        "Indeferida. 'Interceptação exige lastro muito maior que uma simples "
        "quebra de sigilo — não há isso ainda nos autos.' O pedido, mesmo "
        "negado, já alerta o advogado de Marcelo."
    )
    pausa()
    checar_condicoes_automaticas()


def acao_confronto_marcelo():
    if E.preso == 'marcelo':
        imprime(
            "Aviso: ele já está preso e já sabe que é o alvo da investigação — "
            "confrontá-lo agora não muda nada quanto a isso. O risco é outro: "
            "o que ele disser (ou deixar de dizer) pode ser usado a favor ou "
            "contra ele mais adiante."
        )
    elif E.consciencia['marcelo'] == 2:
        imprime(
            "Aviso: ele já sabe que é suspeito — o confronto não vai mudar "
            "isso. Mas dizer na cara dele o que você tem (ou finge ter) é "
            "definitivo e pode alterar o comportamento dele a partir de agora."
        )
    else:
        imprime(
            "Aviso: confrontar agora é definitivo — ele vai saber que é "
            "suspeito, e isso pode mudar o comportamento dele daqui pra frente."
        )
    confirmar = escolha("Confirmar o confronto com Marcelo?", ["Sim, confrontar agora.", "Não, prefiro esperar."])
    if confirmar == 2:
        return
    gastar_dias(1)
    _gatilhar_marcelo()
    E.evidencias.add('confronto_marcelo')
    imprime(
        "Marcelo admite ter ido até o apartamento naquela noite — 'só para "
        "conversar, ela que caiu sozinha' — mas nega qualquer agressão. É uma "
        "admissão parcial de presença, não uma confissão do crime."
    )
    pausa()
    checar_condicoes_automaticas()


def acao_cautelar_diversa():
    alvos = [s for s in ('marcelo', 'rafael', 'camila') if E.consciencia[s] == 2 and E.preso != s]
    if not alvos:
        imprime("Não há, no momento, nenhum suspeito com consciência concreta e solto para pedir cautelar diversa.")
        pausa()
        return
    opcoes = [f"{s.capitalize()}" for s in alvos]
    op = escolha("Contra quem pedir a cautelar diversa (art. 319/320, CPP)?", opcoes)
    suspeito = alvos[op - 1]
    if E.cautelar_diversa[suspeito] is not None:
        imprime("A extensão do art. 320 só pode ser concedida uma vez por partida, e já foi usada para esse suspeito.")
        pausa()
        return
    gastar_dias(1)
    mostrar_aula('cautelar_diversa')
    op2 = escolha(
        "Qual o foco do pedido?",
        [
            "Focada em impedir fuga (art. 320 — retenção de passaporte, alerta de fronteira).",
            "Focada em proteção da vítima/testemunhas (art. 319 — proibição de aproximação).",
        ],
    )
    if op2 == 1:
        E.cautelar_diversa[suspeito] = 'fuga'
        imprime(
            "Deferida. O prazo efetivo do relógio de consciência desse suspeito "
            "passa de 5 para 10 dias."
        )
    else:
        E.cautelar_diversa[suspeito] = 'protecao'
        imprime(
            "Deferida. Protege quem já sofreu ameaça, mas não muda o relógio "
            "de risco de fuga."
        )
    pausa()
    checar_condicoes_automaticas()


def acao_prisao():
    op = escolha(
        "Representar pela prisão de quem?",
        ["Marcelo Nogueira", "Rafael Duarte", "Camila Torres", "Cancelar"],
    )
    if op == 4:
        return
    suspeito = ['marcelo', 'rafael', 'camila'][op - 1]

    imprime(
        f"Representar pela prisão é uma medida formal e séria. Se os elementos "
        f"não sustentarem, ela pode ser contestada — e o prazo do inquérito "
        f"muda a partir de agora, fica mais curto e sem prorrogação."
    )
    confirmar = escolha(f"Confirmar o pedido contra {suspeito.capitalize()}?", ["Sim, confirmar.", "Não, cancelar."])
    if confirmar == 2:
        return

    # checagem de lastro simplificada
    if suspeito == 'marcelo':
        pilares_fechados = sum([pilar1(), pilar2(), pilar3(), pilar4()])
        deferida = pilares_fechados >= 2
    else:
        alibi = E.rafael_alibi if suspeito == 'rafael' else E.camila_descartada
        deferida = not alibi

    gastar_dias(1)
    if suspeito == 'marcelo':
        _gatilhar_marcelo()
    else:
        E.consciencia[suspeito] = 2
        if E.dia_gatilho_concreto[suspeito] is None:
            E.dia_gatilho_concreto[suspeito] = E.dia

    if not deferida:
        imprime("Indeferida — os elementos apresentados não demonstram, neste momento, a necessidade da medida.")
        pausa()
        checar_condicoes_automaticas()
        return

    mostrar_aula('tipo_prisao')
    op2 = escolha(
        "Que tipo de prisão pedir?",
        [
            "Prisão temporária (Lei 7.960/89 — até 10 dias, para quando faltam diligências em andamento).",
            "Prisão preventiva (art. 312/313, CPP — sem prazo próprio, mas ativa o Relógio 2 de 10 dias improrrogáveis).",
        ],
    )
    E.preso = suspeito
    E.tipo_prisao = 'temporaria' if op2 == 1 else 'preventiva'
    E.dia_prisao = E.dia
    imprime(f"Deferida. {suspeito.capitalize()} está preso ({E.tipo_prisao}). O Relógio 2 (10 dias improrrogáveis) começa a contar agora.")
    pausa()
    checar_condicoes_automaticas()


def acao_indiciar():
    indiciar_com_o_que_ha(forcado=False)


# ---------------------------------------------------------------------------
# LOOP PRINCIPAL
# ---------------------------------------------------------------------------

def montar_menu():
    """Retorna uma lista de (rotulo_da_secao, [(texto_opcao, acao), ...]),
    já filtrada pelas mesmas condições de antes — só que agora agrupada,
    pra o jogador ver categorias em vez de uma lista única."""
    testemunhas_pericia = []
    suspeitos = []
    medidas_juridicas = []
    decisoes = []

    if 'porteiro' not in E.evidencias:
        testemunhas_pericia.append(("Conversar com o porteiro Antônio sobre o que ele viu naquela noite.", acao_porteiro))
    if not E.cameras_predio_obtidas:
        testemunhas_pericia.append(("Pedir as câmeras do prédio.", acao_cameras_predio))
    if E.cameras_predio_obtidas and 'camera_waldir' not in E.evidencias:
        testemunhas_pericia.append(("Pedir imagens de câmeras de comércios vizinhos ao prédio.", acao_cameras_vizinhas))
    if 'fechadura_laudo' not in E.evidencias:
        testemunhas_pericia.append(("Pedir laudo pericial sobre a fechadura da porta (trinco automático).", acao_laudo_fechadura))
    if 'beatriz' not in E.evidencias:
        testemunhas_pericia.append(("Procurar Beatriz Lemos (amiga de Helena).", acao_beatriz))

    if not E.camila_visitada:
        suspeitos.append(("Investigar Camila Torres (sócia de Helena).", acao_investigar_camila))
    if not E.rafael_alibi and E.rafael_advogado is False and 'rafael_mentira' not in E.evidencias:
        suspeitos.append(("Investigar Rafael Duarte (irmão de Helena).", acao_investigar_rafael))
    if E.rafael_advogado and not E.rafael_alibi:
        suspeitos.append(("Pedir quebra de sigilo bancário/cartão de Rafael (via formal, já que ele lawyered up).", acao_rafael_sigilo_bancario))
    if 'rafael_mentira' in E.evidencias and not E.rafael_alibi and not E.rafael_advogado:
        suspeitos.append(("Investigar discretamente onde Rafael estava (2 dias).", acao_investigar_rafael_discreto))
    if 'confronto_marcelo' not in E.evidencias:
        suspeitos.append(("Confrontar Marcelo diretamente.", acao_confronto_marcelo))

    if 'sigilo_telefonico_marcelo' not in E.evidencias:
        medidas_juridicas.append(("Sigilo telefônico de Marcelo — quem ligou pra quem e quando, sem ouvir a conversa.", acao_sigilo_telefonico_marcelo))
    if not E.amostra_biologica_marcelo:
        medidas_juridicas.append(("Amostra biológica compulsória de Marcelo — material genético para comparar com a cena.", acao_amostra_biologica_marcelo))
    if 'sangue_dna' not in E.evidencias:
        medidas_juridicas.append(("Comparação de DNA (precisa de amostra biológica já deferida) — lenta, difícil de contestar.", acao_comparacao_dna))
    if 'digital_parcial' not in E.evidencias:
        medidas_juridicas.append(("Impressão digital — rápida, mas pode ser parcial ou antiga.", acao_impressao_digital))
    if 'sigilo_dados_helena' not in E.evidencias:
        medidas_juridicas.append(("Sigilo de dados/nuvem da conta de Helena — mensagens e arquivos de backup.", acao_sigilo_dados_helena))
    if not E.interceptacao_tentada:
        medidas_juridicas.append(("Interceptação telefônica — escuta em tempo real, exige lastro maior.", acao_interceptacao))
    medidas_juridicas.append(("Cautelar diversa (art. 319/320) para algum suspeito já ciente de que é alvo.", acao_cautelar_diversa))

    decisoes.append(("Representar pela prisão de algum suspeito.", acao_prisao))
    decisoes.append(("Encerrar o inquérito e indiciar alguém agora.", acao_indiciar))

    return [
        ("Testemunhas e perícia", testemunhas_pericia),
        ("Suspeitos", suspeitos),
        ("Medidas jurídicas (quebra de sigilo, exames, cautelares)", medidas_juridicas),
        ("Decisões formais", decisoes),
    ]


def loop_principal():
    while not E.jogo_acabou:
        grupos = montar_menu()
        grupos_texto = [(rotulo, [texto for texto, _ in opcoes]) for rotulo, opcoes in grupos]
        print("\n[" + linha_status_tempo() + "]")
        idx = escolha_agrupada(f"O que fazer agora? (dia {E.dia})", grupos_texto)
        # mapeia o índice contínuo de volta para a ação correspondente
        contador = 1
        for _, opcoes in grupos:
            for _, acao in opcoes:
                if contador == idx:
                    acao()
                    contador = -1  # sentinel, já executou
                    break
                contador += 1
            if contador == -1:
                break


def main():
    print("=" * 70)
    print("CASO 001 — O APARTAMENTO 804")
    print("Protótipo jogável v1 — baseado no Mapa de Ramificações v2.1")
    print("=" * 70)
    abertura()
    if not E.jogo_acabou:
        cena_3()
    if not E.jogo_acabou:
        loop_principal()
    print("\nFim de jogo. Rode o script de novo para tentar outro caminho.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nJogo interrompido.")
        sys.exit(0)
