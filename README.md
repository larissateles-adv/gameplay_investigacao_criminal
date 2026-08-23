# O Apartamento 804

Um jogo de investigação criminal por texto em que você é o investigador
responsável por um caso de homicídio — e a única coisa que decide o
desfecho é o que você mesmo conseguir apurar, dentro do prazo.

## Sobre o projeto

Helena Duarte, 34 anos, é encontrada morta em seu apartamento. A porta
estava trancada, sem sinal de arrombamento. Três pessoas do círculo dela
viram nomes citados logo nas primeiras horas — e cabe a você decidir por
onde investigar, quais medidas jurídicas pedir, quando confrontar quem, e
quando o caso está pronto para ser formalizado.

O projeto nasceu da vontade de simular, de forma acessível, como uma
investigação criminal real se constrói: não por uma "resposta certa" escondida
em algum canto do jogo, mas por evidências que se combinam (ou não) para
sustentar uma acusação dentro de prazos processuais reais. É também um
exercício de honestidade narrativa — o mesmo cuidado que se pede de qualquer
peça jurídica: nunca revelar ao jogador algo que ele não investigou, e nunca
deixar dúvida interpretativa virar afirmação.

## Objetivo do jogador

Reunir evidências, decidir quais medidas jurídicas pedir (e quando), e
formalizar um indiciamento contra a pessoa certa, com prova suficiente,
antes que o prazo do inquérito se esgote ou o verdadeiro responsável escape.

Não existe uma única forma de vencer. É possível prender a pessoa errada com
aparência de caso fechado, prender a certa sem prova suficiente para
condenar, deixar o prazo estourar sem decidir nada, ou montar um caso sólido
o bastante para sustentar uma condenação até o fim.

## Como jogar

Em cada momento da investigação, um menu numerado apresenta as ações
disponíveis, agrupadas por tipo (testemunhas e perícia, suspeitos, medidas
jurídicas, decisões formais). A opção **0** mostra a qualquer momento um
resumo do estado atual do caso — prazos, evidências reunidas e situação de
cada suspeito — sem consumir tempo do inquérito.

Toda medida jurídica (quebra de sigilo, prisão, amostra biológica etc.) vem
precedida de uma explicação curta de para que ela serve, dada por um dos
personagens institucionais do jogo (delegado, juíza, promotor, perita). Essa
explicação nunca muda de acordo com o que falta no seu caso específico — o
jogador aprende o instituto jurídico, não a resposta do caso.

## Mecânicas principais

**Investigação livre, sem dicas escondidas.** Toda ação que existe no jogo
está sempre visível em algum menu, mesmo quando bloqueada por fase — o
bloqueio nunca revela o motivo específico, só que "ainda não é o momento".
Nenhuma prova depende de o jogador adivinhar um comando que só existe na
cabeça de quem escreveu o caso.

**Medidas jurídicas sempre tentáveis.** Diferente de diligências de
testemunha/perícia (que desbloqueiam por fase), qualquer medida jurídica pode
ser pedida a qualquer momento — se faltar lastro, ela é indeferida, com
custo de tempo e sem revelar o que faltava. O jogador aprende o requisito
tentando, não lendo um aviso prévio.

**Dois relógios de prazo.** Enquanto o investigado está solto, o inquérito
tem até 30 dias, prorrogáveis uma vez. No momento em que uma prisão é
decretada, o regime muda para 10 dias improrrogáveis a partir da prisão —
prender cedo garante o suspeito, mas trava o relógio.

**Índice de risco de fuga.** A partir do momento em que qualquer suspeito
sabe que é alvo direto de uma medida formal, um relógio próprio começa a
correr. Se ele se esgotar sem prisão nem denúncia, as consequências dependem
de quem é o suspeito — reveladas apenas pelo resultado, nunca pela mecânica
em si.

**Reconstrução dos fatos.** No momento em que o jogador decide formalizar um
indiciamento, o jogo apresenta uma reconstrução da história — mas construída
exclusivamente com as evidências que aquele jogador reuniu, na ordem em que
os fatos aconteceram (contexto anterior ao crime, a noite do crime, e o que
a investigação levantou depois). Pontos sem evidência aparecem marcados
explicitamente como não esclarecidos, nunca preenchidos com informação que o
jogador não descobriu. É a versão dos fatos que a própria investigação do
jogador consegue sustentar — não um gabarito do caso.

## Fluxo de uma partida

1. **Cena de abertura** — duas decisões guiadas (preservar a cena x agir
   rápido; interrogar o porteiro x pedir câmeras) que já custam tempo e
   moldam o que fica disponível depois.
2. **Círculo da vítima** — o jogador escolhe por qual suspeito começar,
   sempre por decisões binárias em sequência.
3. **Investigação livre** — menu agrupado com testemunhas/perícia,
   suspeitos, medidas jurídicas e decisões formais, disponível até que o
   jogador decida prender ou indiciar, ou até o prazo se esgotar.
4. **Decisão formal** — representar por prisão e/ou formalizar o
   indiciamento contra alguém (ou encerrar sem indiciar ninguém).
5. **Reconstrução dos fatos** — apresentada no momento do indiciamento, com
   base só no que foi investigado.
6. **Denúncia → pronúncia → veredito** — sequência narrativa curta em que o
   Ministério Público e a juíza reavaliam os mesmos elementos que o jogador
   reuniu, decidindo a capitulação final e o resultado do julgamento.

## Arquitetura e tecnologias

- **`caso001.py`** — motor do jogo em Python puro (sem dependências
  externas), rodável em terminal. Toda a lógica de estado, evidências,
  prazos e finais vive aqui.
- **Interface web** — em desenvolvimento com [Streamlit](https://streamlit.io),
  reaproveitando o mesmo motor de jogo sem duplicar a lógica (ver seção
  "Estado atual" abaixo).

## Estrutura do projeto

```
.
├── caso001.py                          # motor do jogo (terminal)
├── streamlit_app.py                    # interface web (Streamlit)
├── README.md                           # este arquivo
└── docs/
    └── design_e_verdade_do_caso.md     # documento interno com spoilers —
                                         # verdade objetiva do caso, pesos de
                                         # evidência e regras de bastidor
```

## Como rodar

### Terminal

```bash
python3 caso001.py
```

Requer apenas Python 3 — sem dependências externas.

### Web (Streamlit)

```bash
pip install streamlit
streamlit run streamlit_app.py
```

## Estado atual

- Lógica de investigação, prazos, medidas jurídicas e finais: completa e
  jogável de ponta a ponta pelo terminal.
- Reconstrução dos fatos baseada no conhecimento do jogador: implementada.
- Interface web: em construção, reaproveitando o motor do terminal sem
  duplicar a lógica de estado.

## Limitações conhecidas

- Personagens de textura (mãe da vítima, ex-funcionário, motorista de
  aplicativo, vizinhos) ainda não têm cena própria — existem apenas como
  elenco planejado.
- A fase processual pós-inquérito (denúncia, pronúncia, plenário) é
  representada de forma condensada, não como simulação completa de rito.
- Interceptação telefônica está implementada de forma simplificada nesta
  versão (sempre indeferida, por design).

## Próximos passos

- Finalizar a interface web e publicar um link de acesso gratuito para
  teste.
- Dar cena própria aos personagens de textura já mapeados.
- Avaliar expandir a mecânica de cautelar diversa (violação da medida como
  gatilho de nova prisão).

---

Detalhes de spoiler sobre o caso (verdade objetiva, pesos de evidência,
base jurídica completa) estão documentados separadamente em
[`docs/design_e_verdade_do_caso.md`](docs/design_e_verdade_do_caso.md), para
quem quiser entender o funcionamento interno sem estragar a experiência de
quem for jogar.
