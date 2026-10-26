# ************************************************
#   Cenario.py
#   Dados geometricos do trabalho: o conjunto de triangulos, gerado
#   aleatoriamente (com semente) ou lido de arquivo, e a grade de
#   aceleracao construida sobre ele.
#
#   Formato de arquivo (linhas iniciadas por '#' sao comentarios):
#       N
#       x1 y1 x2 y2 x3 y3      <- uma linha por triangulo, N linhas
# ************************************************

import math
import random
import time

from Ponto import Ponto
from Triangulo import Triangulo
from Grade import Grade
from ListaDeCoresRGB import Gray

# Triangulos com Qualidade() abaixo deste valor sao quase degenerados:
# a tolerancia do teste detalhado os "esticaria" para alem do envelope.
QUALIDADE_MINIMA = 1e-3


class Cenario:
    def __init__(self, triangulos, origem, semente=None, tamanho=None, Min=None, Max=None):
        if not triangulos:
            raise ValueError("O cenario precisa ter pelo menos um triangulo")
        self.Triangulos = triangulos
        self.Origem = origem          # "aleatorio" ou nome do arquivo
        self.Semente = semente
        self.Tamanho = tamanho
        self.Grade = None
        self.TempoGrade = 0.0

        # Area de visualizacao: a informada ou os envelopes com 5% de folga
        if Min is None or Max is None:
            x0 = min(T.Envelope[0].x for T in triangulos)
            y0 = min(T.Envelope[0].y for T in triangulos)
            x1 = max(T.Envelope[1].x for T in triangulos)
            y1 = max(T.Envelope[1].y for T in triangulos)
            folga = 0.05 * max(x1 - x0, y1 - y0, 1e-6)
            Min, Max = Ponto(x0 - folga, y0 - folga), Ponto(x1 + folga, y1 + folga)
        self.Min = Min
        self.Max = Max

    # **********************************************************************
    # ConstroiGrade(nx, ny)
    #      (Re)constroi a grade e mede o tempo de construcao.
    # **********************************************************************
    def ConstroiGrade(self, nx, ny):
        inicio = time.perf_counter()
        self.Grade = Grade(self.Triangulos, nx, ny)
        self.TempoGrade = time.perf_counter() - inicio
        return self.Grade

    def Descricao(self):
        if self.Origem == "aleatorio":
            return "aleatorio semente=%s tamanho=%s" % (self.Semente, self.Tamanho)
        return "arquivo %s" % self.Origem


# **********************************************************************
# GeraAleatorio(n, semente, tamanho, Min, Max)
#      Gera n triangulos. Cada um tem centro sorteado em [Min, Max] e
#      vertices sorteados num quadrado de lado 2*tamanho ao redor do centro.
#      Usa um gerador proprio (random.Random) para que a mesma semente
#      produza sempre o mesmo cenario.
# **********************************************************************
def GeraAleatorio(n, semente, tamanho, Min=None, Max=None):
    if n < 1 or not tamanho > 0:
        raise ValueError("GeraAleatorio: precisa de n >= 1 e tamanho > 0")
    Min = Min or Ponto(-10, -5)
    Max = Max or Ponto(10, 5)
    rng = random.Random(semente)
    triangulos = []
    tentativas = 0
    while len(triangulos) < n:
        tentativas += 1
        if tentativas > 1000 * n:
            raise ValueError("GeraAleatorio: tamanho %g gera so triangulos degenerados" % tamanho)
        cx = rng.uniform(Min.x, Max.x)
        cy = rng.uniform(Min.y, Max.y)
        P = [Ponto(cx + rng.uniform(-tamanho, tamanho), cy + rng.uniform(-tamanho, tamanho))
             for _ in range(3)]
        T = Triangulo(P[0], P[1], P[2], Gray)
        if T.Qualidade() >= QUALIDADE_MINIMA:
            triangulos.append(T)
    return Cenario(triangulos, "aleatorio", semente, tamanho, Min, Max)


# **********************************************************************
# LeArquivo(nome)
#      Le um cenario no formato descrito no inicio do arquivo.
#      Triangulos quase degenerados sao descartados com aviso.
# **********************************************************************
def LeArquivo(nome):
    with open(nome, encoding="utf-8") as f:
        tokens = []
        for linha in f:
            linha = linha.split("#", 1)[0]
            tokens.extend(linha.split())

    try:
        n = int(tokens[0])
        valores = [float(v) for v in tokens[1:]]
    except (IndexError, ValueError):
        raise ValueError("%s: formato invalido (esperado N e N linhas com 6 numeros)" % nome)
    if n < 1 or not all(math.isfinite(v) for v in valores):
        raise ValueError("%s: N precisa ser >= 1 e as coordenadas, numeros finitos" % nome)
    if len(valores) < 6 * n:
        raise ValueError("%s: esperados %d triangulos, encontrados %d" % (nome, n, len(valores) // 6))

    triangulos = []
    for i in range(n):
        x1, y1, x2, y2, x3, y3 = valores[6 * i: 6 * i + 6]
        T = Triangulo(Ponto(x1, y1), Ponto(x2, y2), Ponto(x3, y3), Gray)
        if T.Qualidade() < QUALIDADE_MINIMA:
            print("Aviso: triangulo %d de %s descartado (degenerado)" % (i, nome))
            continue
        triangulos.append(T)
    return Cenario(triangulos, nome)


# **********************************************************************
# SalvaArquivo(cenario, nome)
#      Grava o cenario no mesmo formato lido por LeArquivo.
# **********************************************************************
def SalvaArquivo(cenario, nome):
    with open(nome, "w", encoding="utf-8") as f:
        f.write("# %s\n%d\n" % (cenario.Descricao(), len(cenario.Triangulos)))
        for T in cenario.Triangulos:
            f.write(" ".join("%.17g %.17g" % (V.x, V.y) for V in T.Vertices) + "\n")
