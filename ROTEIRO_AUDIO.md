# Roteiro do áudio – `video/demo.mp4` (2:00)

Cada bloco começa no instante indicado e precisa caber até o próximo. O texto foi dimensionado para cerca de 2,5 palavras por segundo, um ritmo calmo. Se terminar antes, deixe silêncio até o próximo bloco. A coluna "Na tela" diz o que aparece, para servir de referência.

**Como gravar:** abra o `demo.mp4` num player, sem som, ao lado do Audacity. Aperte gravar no Audacity e, logo em seguida, play no vídeo. No fim, corte o início do áudio no Audacity até a primeira fala coincidir com 0:00. Exporte como `narracao.wav` e rode `python ferramentas/video.py --audio narracao.wav`.

| Início | Duração | Na tela | Fala |
|---|---|---|---|
| 0:00 | 10 s | Cenário com 150 triângulos; console com `semente=1` | Trabalho 1 de Computação Gráfica, de Humberto Corrêa e Pedro Idalencio. São 150 triângulos aleatórios, gerados com a semente 1. |
| 0:10 | 12 s | Cursor arrastando o ponto; depois as setas → e ↑ | O ponto se move clicando e arrastando com o mouse, ou pelas setas. A cada movimento, a consulta é refeita e a posição aparece no painel e no console. |
| 0:22 | 7 s | Ponto parado sobre dois triângulos vermelhos | Agora o ponto está sobre dois triângulos. Amarelo é a célula da grade; azul, os candidatos da grade. |
| 0:29 | 7 s | Tecla `b`: envelopes roxos aparecem e somem | Laranja são os aprovados no envelope, e vermelho os que contêm o ponto. A tecla B mostra os envelopes. |
| 0:36 | 9 s | Teclas `g` e `c`: grade e candidatos somem e voltam | A tecla G esconde a grade, e a tecla C, os candidatos. Os contadores não mudam: a visualização não altera o resultado. |
| 0:45 | 6 s | Tecla `1`: força bruta, 150 testes | Tecla 1: força bruta. São 150 testes detalhados, e dois triângulos contêm o ponto. |
| 0:51 | 6 s | Tecla `2`: só envelope, 4 testes | Tecla 2: só envelopes. Quatro passam no envelope, quatro testes, mesmo resultado. |
| 0:57 | 6 s | Tecla `3`: só grade, 9 testes | Tecla 3: só a grade. Nove candidatos, nove testes, os mesmos dois triângulos. |
| 1:03 | 5 s | Tecla `4`: grade + envelope, 4 testes | Tecla 4: grade e envelope. Só quatro testes. |
| 1:08 | 12 s | Teclas `+` `+` (grade 64×32) e depois `-` `-` | As teclas mais e menos mudam a resolução da grade. Em 64 por 32, a grade sozinha já deixa só quatro candidatos. Depois, volto para 16 por 8. |
| 1:20 | 10 s | Cenário com 20 mil triângulos; tecla `1`, tempo de 15.611 µs | Agora, 20 mil triângulos. Na força bruta, são 20 mil testes e cerca de 15 milissegundos por consulta. |
| 1:30 | 8 s | Tecla `4`: 9 testes, 87 µs | Com grade e envelope, só nove testes e menos de 0,1 milissegundo, com o mesmo resultado. |
| 1:38 | 12 s | Terminal: `python Testes.py` e `OK: todos os testes passaram` | Os testes automáticos conferem que as quatro configurações dão sempre o resultado da força bruta, inclusive com pontos sobre arestas e vértices, que contam como dentro. |
| 1:50 | 10 s | Relatório rolando nas tabelas de resultados | O relatório compara as configurações variando quantidade, semente, tamanho, grade e posição dos pontos. Obrigado. |
