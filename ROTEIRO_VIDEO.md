# Roteiro do vídeo (até 2 min)

Objetivo: mostrar cada item do enunciado funcionando, na ordem em que aparece na especificação.

## Preparação (antes de gravar)

1. Abra dois terminais em `trabalho/` lado a lado com a janela do programa, para o console aparecer no vídeo.
2. Deixe as janelas abertas antes de gravar. Trocar de janela é mais rápido que reiniciar o programa:
   - **Janela A:** `python ProgramaT1.py --n 150 --tamanho 1.2 --semente 1`
   - **Janela B:** `python ProgramaT1.py --n 20000 --tamanho 0.3 --grade 64 32` (minimizada)
   - **Terminal livre** com `python Testes.py` digitado, sem apertar Enter.
3. Na janela A, ache antes um ponto onde 2 triângulos se cruzam. Perto de (5,17; −1,17), à direita e abaixo do centro, há um, mostrado na Figura 1 do relatório. Com as setas, ajuste até o painel mostrar `Contem o ponto: 2`.
4. Gravação: Ferramenta de Captura (`Win+Shift+R`), com a região cobrindo a janela e o console.

## Roteiro

| Tempo | O que fazer | O que falar |
|---|---|---|
| 0:00–0:10 | Janela A aberta. Mostrar no console a linha `Cenario: aleatorio semente=1 ...` | "Trabalho 1 de CG, Humberto e Pedro. 150 triângulos aleatórios gerados com semente 1. A mesma semente gera sempre o mesmo cenário." |
| 0:10–0:22 | Clicar em vários pontos, arrastar com o botão esquerdo, usar as setas | "O ponto é controlado por mouse e setas. A posição aparece no painel e no console, com uma linha por consulta." |
| 0:22–0:45 | Levar o ponto ao cruzamento preparado. Apontar a célula amarela, os triângulos azuis, os laranjas e os vermelhos. Apertar `b` (envelopes), `b` de novo, depois `g` e `c` | "Amarelo é a célula da grade que contém o ponto. Azul são os candidatos da grade, laranja os aprovados no envelope, vermelho os que contêm o ponto. Grade, envelopes e candidatos podem ser escondidos, e os contadores não mudam." |
| 0:45–1:08 | Com o ponto parado, apertar `1`, `2`, `3`, `4` devagar, apontando "Testes detalhados" e "Contem o ponto" | "As quatro configurações: força bruta com 150 testes, só envelope, só grade e grade com envelope com 4 testes. O resultado é sempre o mesmo. As teclas `s` e `e` ligam e desligam cada etapa." |
| 1:08–1:20 | Apertar `+` duas vezes, depois `-` duas vezes | "A resolução da grade é configurável. Com 64×32 a grade sozinha já deixa só 4 candidatos." |
| 1:20–1:38 | Trocar para a janela B. Apertar `1`, mostrar o tempo; apertar `4`, mostrar o tempo | "Com 20 mil triângulos, a força bruta leva cerca de 15 milissegundos por consulta. Com grade e envelope, menos de 0,1 milissegundo, com o mesmo resultado." |
| 1:38–1:50 | No terminal, Enter em `python Testes.py` e mostrar `OK: todos os testes passaram` | "Os testes conferem que as quatro configurações dão o mesmo resultado da força bruta, inclusive para pontos sobre arestas e vértices, que contam como dentro graças à tolerância numérica." |
| 1:50–2:00 | Mostrar rapidamente o `RELATORIO.pdf` aberto na seção 6 | "O relatório traz a comparação variando quantidade, semente, tamanho, grade e posição dos pontos. Obrigado." |

## Se sobrar tempo (ou num segundo take)

- `w` salva o cenário em `cenarios/`, e `--arquivo` o reabre: mostra a leitura de arquivo.
- `python ProgramaT1.py --arquivo cenarios/exemplo.txt --grade 4 2`: cenário lido de arquivo, com triângulos que compartilham vértices.

## Itens do enunciado cobertos

Cenário aleatório com semente (0:00), controle do ponto e posição exibida (0:10), categorias com cores e toggles (0:22), as 4 configurações com o mesmo resultado (0:45), parametrização da subdivisão (1:08), desempenho e contadores (todo o vídeo; 1:20), aresta/vértice com tolerância (1:38) e comparação no relatório (1:50).
