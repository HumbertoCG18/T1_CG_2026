# Inclusão de ponto em triângulos com aceleração

Trabalho I de Fundamentos de Computação Gráfica (PUCRS, 2026/2), de Humberto Corrêa e Pedro Idalencio.

O programa mostra N triângulos e um ponto controlado por mouse ou teclado. A cada movimento, ele encontra todos os triângulos que contêm o ponto. A busca combina até três etapas:

1. **Grade regular** (subdivisão espacial): só os triângulos da célula do ponto viram candidatos.
2. **Envelope (AABB):** descarta os candidatos cuja caixa não contém o ponto.
3. **Teste detalhado:** a orientação do ponto em relação às três arestas, com tolerância numérica (ponto sobre aresta ou vértice conta como dentro).

As etapas 1 e 2 podem ser ligadas e desligadas durante a execução, e as quatro combinações sempre devem dar o mesmo resultado da força bruta.

## Como rodar

Requisitos: Python 3, `PyOpenGL` e freeglut.

```bash
cd trabalho
python ProgramaT1.py                                  # 1000 triângulos aleatórios, semente 1
python ProgramaT1.py --n 5000 --semente 7 --grade 32 16
python ProgramaT1.py --arquivo cenarios/exemplo.txt --grade 4 2
python Testes.py                                      # confere as 4 configurações contra a força bruta
python Benchmark.py                                   # gera resultados/benchmark.md e .csv
```

Teclas principais: `1`–`4` trocam a configuração, `s`/`e` ligam e desligam grade e envelope, `g`/`b`/`c` mostram grade, envelopes e candidatos, `+`/`-` mudam a resolução da grade. A tecla `h` lista todas.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `trabalho/` | código entregue: geometria, grade, consulta, visualização, testes e benchmark |
| `trabalho/RELATORIO.md` / `.pdf` | relatório com o mapeamento dos requisitos e a análise de desempenho |
| `ferramentas/` | scripts que geram as capturas, o PDF, o vídeo e a trilha de fundo |

## Resultado em uma linha

Com 1000 triângulos, grade 16×8 + envelope responde cerca de 60× mais rápido que a força bruta. O ganho cai com triângulos grandes ou com uma grade grossa ou fina demais; a discussão completa está na seção 7 do relatório.
