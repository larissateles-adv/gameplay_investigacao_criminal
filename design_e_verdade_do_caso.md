# Documento de design — Caso 001: O Apartamento 804

> ⚠️ **Este documento contém spoilers completos do caso**, incluindo a
> identidade do culpado, o motivo real e a força de cada evidência. Ele existe
> para quem mantém ou revisa o jogo, não para quem vai jogá-lo. Se você
> pretende jogar, pare aqui e volte para o [README](../README.md).

Este é o material de bastidor por trás do Caso 001. O jogo em si (`caso001.py`
e, futuramente, a versão web) nunca expõe este conteúdo diretamente — a
"verdade objetiva" abaixo não aparece em nenhum texto que o jogador vê. O que
o jogador vê é sempre uma consequência dela, revelada evidência por
evidência, conforme ele investiga.

---

## 1. A verdade objetiva do caso

Helena Duarte terminou o relacionamento com Marcelo Nogueira três semanas
antes do crime. Marcelo não aceitou. Nos últimos dias, ele descobriu que
Helena estava reunindo mensagens e prints para pedir uma medida protetiva
contra ele.

Às 21h21, Marcelo ligou pedindo para se verem "uma última vez". Às 21h37
entrou no prédio (visto por Antônio, o porteiro). Subiu, discutiram, Helena
derrubou a taça no confronto e Marcelo se cortou ao segurar o caco (daí o
sangue dele na taça, não dela). Ele a empurrou; ela bateu a cabeça na quina
do rack. A morte não foi plenamente premeditada, mas houve dolo eventual: ele
viu que ela sangrava, a deixou lá, levou o celular dela (que continha as
provas da medida protetiva) e desceu de elevador às 22h16 — a mesma descida
já registrada pelas câmeras, não há um segundo trajeto. Ao sair, ele apenas
puxou a porta atrás de si: a fechadura do apartamento é de trinco automático
(mola), tranca sozinha ao fechar, sem exigir chave por fora. Por isso a porta
é encontrada trancada e sem sinal de arrombamento, mesmo Marcelo nunca tendo
tido cópia da chave.

A câmera do elevador registra a descida, mas com baixa definição — só
silhueta compatível, sem reconhecimento de rosto. A câmera do saguão/rua
(que confirmaria a saída do prédio) estava com defeito naquela noite.
Antônio não percebeu a saída porque estava atendendo outra pessoa na
portaria naquele intervalo — falha de atenção, não inconsistência criada de
propósito.

A impressão digital parcial na taça, se comparada, pode até "bater" com
Marcelo — mas ele e Helena namoraram até três semanas antes, então uma
digital antiga dele em objetos da casa é esperada e facilmente contestável em
juízo como resíduo de visita anterior. É uma prova estruturalmente fraca por
natureza, não por acaso do roteiro.

**Rafael é inocente.** O "conflito financeiro" era uma discussão antiga e já
resolvida sobre a herança dos pais, sem relação com o crime. Ele mentiu sobre
um detalhe — não sobre o crime, mas porque estava com um caso extraconjugal e
não queria explicar por que só chegou ao prédio às 23h18 vindo de outro
lugar. Ao ser questionado, ele errou de propósito o horário que afirmou ter
chegado (23h06), tentando encurtar a distância entre onde estava de verdade e
quando chegou — sem saber que a portaria já tinha o horário exato registrado.

**Camila é inocente.** A disputa societária era real, mas ela estava em um
jantar de negócios com três testemunhas e nota fiscal de cartão até às
23h05, em outro bairro.

**Beatriz Lemos**, amiga próxima de Helena, sabe que Helena andava com medo
de Marcelo nas últimas semanas e estava "guardando print de tudo" para pedir
uma medida protetiva — um caminho testemunhal até o motivo real, sem
depender só de quebra de sigilo de dados.

**Seu Waldir**, dono da farmácia em frente ao prédio, tem câmera própria
voltada para a rua. Sua gravação mostra o carro de Marcelo saindo às 22h19 —
a prova que liga a descida do elevador a Marcelo efetivamente deixando o
local.

---

## 2. Elenco e papel real de cada um

| Personagem | Papel na trama | Função no jogo |
|---|---|---|
| Marcelo Nogueira (ex-companheiro) | **Culpado real** | Alvo correto, mas só condenável com prova material — motivo e oportunidade sozinhos não bastam |
| Rafael Duarte (irmão) | Inocente | A armadilha central: todo sinal comportamental aponta pra ele, mas nenhuma prova material o liga ao crime |
| Camila Torres (sócia) | Inocente | Suspeita-tutorial: motivo real, zero oportunidade, descartável com uma diligência simples |
| Beatriz Lemos (amiga de Helena) | Testemunha | Caminho alternativo até o motivo real, sem depender de perícia digital |
| Seu Waldir (farmácia vizinha) | Testemunha | Fonte da câmera externa que resolve a lacuna da câmera do saguão |
| Antônio (porteiro) | Testemunha | Confirma a entrada; não viu a saída por distração, não por falha do sistema |
| Cristiane Duarte (mãe) | Textura | Emocional; pode reforçar ou desconstruir a suspeita sobre Rafael, sem provar nada — sem cena própria ainda |
| Diego Fonseca (ex-funcionário) | Isca secundária | Motivo superficial, zero oportunidade — sem cena própria ainda |
| Sérgio Paixão (motorista de app) | Textura | Pode confirmar/contradizer horários — sem cena própria ainda |
| Zuleide, Junior | Ruído puro | Existem para o jogador aprender a filtrar sinal de ruído — sem cena própria ainda |

---

## 3. Catálogo de evidências (peso e a quem apontam)

| Evidência | Peso | Aponta para | Observação |
|---|---|---|---|
| Sangue na taça vs. DNA de Marcelo | Forte | Marcelo | Fecha sozinha o pilar de conexão material |
| Impressão digital parcial na taça | Fraca | Inconclusiva sozinha | Contestável como resíduo de visita anterior ao término do namoro |
| Câmeras do prédio (entrada 21h37 / elevador 22h16) | Média | Cronologia | Confirma o trajeto interno, não confirma quem saiu (câmera do saguão com defeito) |
| Câmera da farmácia (Seu Waldir, carro às 22h19) | Forte | Marcelo | Só aparece se o jogador pensar em pedir câmeras vizinhas, não só do prédio |
| Ligação de Marcelo às 21h21 (47s) | Média | Marcelo | Prova contato, não presença dentro do apartamento |
| Mensagens da nuvem de Helena + último ping de localização dela | Forte | Marcelo (motivo) | Uma única medida (sigilo de dados) devolve as duas coisas juntas |
| Depoimento de Beatriz Lemos | Média | Marcelo (motivo) | Caminho testemunhal alternativo ao sigilo de dados |
| Testemunho do porteiro (homem, 1,80m, boné) | Fraca | Genérico | Só útil combinado com outra prova |
| Mentira de Rafael sobre o horário | Média (pista falsa) | Parece Rafael | Se investigada a fundo, vira o próprio álibi dele |
| Disputa de herança (Rafael) | Fraca (pista falsa) | Parece Rafael | Motivo antigo, sem escalada recente |
| Disputa societária (Camila) | Fraca (pista falsa) | Parece Camila | Cai com uma única diligência (nota fiscal + testemunhas) |
| Laudo da fechadura de trinco automático | — | Explica a cena | Justifica a porta trancada sem arrombamento |

---

## 4. Estrutura de prova contra Marcelo — os quatro pilares

O caso contra Marcelo não depende de um número fixo de evidências, mas de
fechar quatro frentes estruturais. Cada uma pode ser satisfeita por mais de
uma combinação de evidências — por isso existem vários caminhos até o mesmo
resultado forte:

1. **Presença/oportunidade** — câmeras do prédio + porteiro, OU câmera do
   Waldir, OU admissão no confronto direto.
2. **Vínculo com a vítima** — depoimento de Beatriz, OU mensagens da medida
   protetiva, OU a ligação das 21h21 combinada com o histórico do
   relacionamento.
3. **Conexão material com a cena** — DNA do sangue (fecha sozinho), OU o
   ping de localização de Helena combinado com a digital parcial (caminho
   mais fraco e contestável — o ping sozinho reforça, mas não fecha).
4. **Circunstância que fecha a cronologia** — câmera do Waldir explicando a
   saída, OU laudo da fechadura explicando a porta trancada, OU o resultado
   do DNA explicando de quem é o sangue.

A **classificação do crime** (feminicídio, art. 121-A, CP, ou homicídio
simples, art. 121, CP) depende separadamente da prova do elemento de gênero
do art. 121-A, §1º — satisfeita pelo depoimento de Beatriz e/ou pelas
mensagens da medida protetiva. Fechar os quatro pilares prova a autoria;
fechar o elemento de gênero decide o tipo penal.

---

## 5. Tabela de finais

| Final | Condição |
|---|---|
| **1a** — Condenação por feminicídio (art. 121-A) | 4 pilares fechados + elemento de gênero provado, dentro do prazo original, sem dilação |
| **1b** — Condenação por homicídio simples (art. 121) | Autoria completa, mas sem prova do elemento de gênero, ou autoria só fechada após dilação de prazo |
| **2** — Absolvido por insuficiência probatória | Marcelo indiciado, mas algum dos 4 pilares está em aberto |
| **3** — Condenação de inocente | Rafael ou Camila indiciado e levado a julgamento sem álibi resolvido |
| **4** — Prazo esgotado sem acusação | Relógio 1 (30 dias) estourado sem prisão nem indiciamento |
| **5a** — Prisão relaxada por excesso de prazo | Preso, Relógio 2 (10 dias) estourado sem denúncia, relaxamento puro |
| **5b** — Conversão em cautelar diversa | Mesma situação do 5a, mas com pedido ativo de cautelar em vez do relaxamento puro |
| **6** — Marcelo foge | Índice de risco de fuga (5 dias após ele saber que é alvo, ou 10 com cautelar de fuga) esgotado sem prisão nem denúncia |
| Indiciamento rejeitado pelo MP | Jogador indicia Rafael ou Camila depois que o próprio álibi de cada um já foi confirmado nos autos |

Todos os finais partem da mesma verdade objetiva fixa (Seção 1) — nenhum
deles reescreve o que aconteceu, só o que o jogador conseguiu (ou não) provar
a tempo.

---

## 6. Base jurídica de referência

- **Art. 10, CPP** — prazo do inquérito: 10 dias se o indiciado está preso
  (contados da prisão), improrrogável; 30 dias se solto, prorrogável uma vez
  mediante pedido fundamentado.
- **Art. 312 e 313, III, CPP** — prisão preventiva exige indícios de autoria
  e materialidade + necessidade (aqui, garantia da execução de medida
  protetiva de urgência, já que Helena estava reunindo provas para pedir
  uma).
- **Lei 14.994/2024 — feminicídio (art. 121-A, CP)** — crime autônomo,
  distinto do homicídio (art. 121), em vigor desde 9/10/2024. Não é mais
  qualificadora do art. 121, §2º (revogado). Pena de reclusão de 20 a 40
  anos, crime hediondo.
- **Simplificação assumida:** a fase pós-inquérito (denúncia, pronúncia e
  plenário) é representada como uma sequência narrativa curta e condensada —
  a precisão jurídica é mantida na fase de inquérito (a parte jogável) e na
  classificação do crime, não numa simulação completa de rito processual.

---

## 7. Simplificações conscientes da versão atual

- Interceptação telefônica sempre indefere nesta versão — existe só para o
  jogador aprender o risco de pedir uma medida sem lastro suficiente.
- Cautelar diversa (art. 319/320) é uma escolha binária de foco (fuga x
  proteção), sem sub-mecânica de violação da medida.
- A dilação de prazo libera as diligências ainda disponíveis no menu normal,
  em vez de um conjunto fixo de pistas categorizadas.
- Os personagens de textura (Cristiane, Diego, Sérgio, Zuleide, Junior) ainda
  não têm cena própria — ver Seção 2.
