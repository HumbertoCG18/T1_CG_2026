# ************************************************
#   Benchmark.py
#   Experimentos do relatorio, sem janela. Varia um fator por vez a partir
#   de uma configuracao base e executa as 4 configuracoes sobre os MESMOS
#   cenarios e os MESMOS pontos de consulta. Confere cada resultado com a
#   forca bruta.
#
#   Uso: python Benchmark.py [--rapido]
#   Saida: resultados/benchmark.csv e resultados/benchmark.md
# ************************************************

import argparse
import csv
import os
import random
import time

from Ponto import Ponto
from Cenario import GeraAleatorio, LeArquivo
from Consulta import Consulta, CONFIGURACOES

BASE = dict(n=1000, semente=1, tamanho=1.0, grade=(16, 8), pontos="uniforme")

FATORES = [
    ("n", [100, 1000, 5000, 20000]),
    ("semente", [1, 2, 3]),
    ("tamanho", [0.2, 1.0, 3.0, 6.0]),
    ("grade", [(1, 1), (4, 2), (16, 8), (64, 32), (128, 64)]),
    ("pontos", ["uniforme", "centroides", "fora"]),
    ("arquivo", ["cenarios/exemplo.txt"]),
]

PASTA = os.path.dirname(os.path.abspath(__file__))


# **********************************************************************
# PontosDeConsulta(cenario, tipo, quantidade)
#      uniforme:   sorteados na area do cenario
#      centroides: centroides de triangulos sorteados (sempre contidos)
#      fora:       sorteados numa faixa fora da grade (nenhum triangulo)
#      A semente e fixa para que todas as configuracoes usem os mesmos pontos.
# **********************************************************************
def PontosDeConsulta(cenario, tipo, quantidade):
    rng = random.Random(999)
    if tipo == "uniforme":
        return [Ponto(rng.uniform(cenario.Min.x, cenario.Max.x),
                      rng.uniform(cenario.Min.y, cenario.Max.y)) for _ in range(quantidade)]
    if tipo == "centroides":
        pontos = []
        for _ in range(quantidade):
            A, B, C = rng.choice(cenario.Triangulos).Vertices
            pontos.append(Ponto((A.x + B.x + C.x) / 3, (A.y + B.y + C.y) / 3))
        return pontos
    G = cenario.Grade
    return [Ponto(rng.uniform(G.Min.x, G.Max.x), G.Max.y + rng.uniform(0.1, 1.0))
            for _ in range(quantidade)]


# **********************************************************************
# Mede(cenario, pontos, repeticoes)
#      Executa as 4 configuracoes intercaladas, ponto a ponto, para que um
#      pico de carga da maquina afete todas igualmente. Para cada ponto e
#      configuracao guarda o menor tempo entre as repeticoes.
#      Devolve {nome: (medias, resultados)}.
# **********************************************************************
def Mede(cenario, pontos, repeticoes):
    melhor = {nome: [None] * len(pontos) for nome, _, _ in CONFIGURACOES}
    for _ in range(repeticoes):
        for k, P in enumerate(pontos):
            for nome, usaGrade, usaEnvelope in CONFIGURACOES:
                r = Consulta(cenario, P, usaGrade, usaEnvelope)
                if melhor[nome][k] is None or r.Tempo < melhor[nome][k].Tempo:
                    melhor[nome][k] = r

    saida = {}
    n = len(pontos)
    for nome, usaGrade, usaEnvelope in CONFIGURACOES:
        R = melhor[nome]
        medias = dict(
            grade=sum(len(r.CandGrade) for r in R) / n if usaGrade else None,
            envelope=sum(len(r.CandEnvelope) for r in R) / n if usaEnvelope else None,
            testes=sum(r.Testes for r in R) / n,
            contem=sum(len(r.Contem) for r in R) / n,
            tempo=sum(r.Tempo for r in R) / n,
        )
        saida[nome] = (medias, [sorted(r.Contem) for r in R])
    return saida


def Executa(rapido):
    quantidade, repeticoes = (30, 1) if rapido else (100, 5)
    linhas = []

    for fator, valores in FATORES:
        for valor in valores:
            p = dict(BASE)
            if fator == "arquivo":
                p.update(n=None, semente=None, tamanho=None)
            p[fator] = valor

            if fator == "arquivo":
                cenario = LeArquivo(os.path.join(PASTA, valor))
            else:
                cenario = GeraAleatorio(p["n"], p["semente"], p["tamanho"])
            # menor de 3 construcoes, pelo mesmo motivo do menor tempo de consulta
            tempoGrade = min(cenario.ConstroiGrade(*p["grade"]) and cenario.TempoGrade
                             for _ in range(3))
            media, maximo, total = cenario.Grade.Estatisticas()
            pontos = PontosDeConsulta(cenario, p["pontos"], quantidade)

            medicoes = Mede(cenario, pontos, repeticoes)
            tempoBruta = medicoes["forca bruta"][0]["tempo"]
            referencia = medicoes["forca bruta"][1]
            for nome, _, _ in CONFIGURACOES:
                medias, resultados = medicoes[nome]
                divergencias = sum(a != b for a, b in zip(resultados, referencia))
                if divergencias:
                    raise AssertionError("%s divergiu da forca bruta em %d pontos (%s=%s)"
                                         % (nome, divergencias, fator, valor))
                linhas.append(dict(
                    fator=fator, valor=valor if fator != "grade" else "%dx%d" % valor,
                    triangulos=len(cenario.Triangulos), semente=p["semente"], tamanho=p["tamanho"],
                    grade="%dx%d" % p["grade"], pontos=p["pontos"], config=nome,
                    cand_grade=medias["grade"], cand_envelope=medias["envelope"],
                    testes=medias["testes"], contem=medias["contem"],
                    tempo_us=medias["tempo"] * 1e6,
                    speedup=tempoBruta / medias["tempo"] if medias["tempo"] > 0 else None,
                    construcao_grade_ms=tempoGrade * 1e3,
                    indices_por_celula=media, max_por_celula=maximo, indices_total=total,
                ))
            print("%-8s %-22s ok (%d pontos, 4 configuracoes iguais a forca bruta)"
                  % (fator, linhas[-1]["valor"], len(pontos)))
    return linhas


def Formata(v, casas=1):
    if v is None:
        return "-"
    if isinstance(v, float):
        return "%.*f" % (casas, v)
    return str(v)


def Grava(linhas):
    pasta = os.path.join(PASTA, "resultados")
    os.makedirs(pasta, exist_ok=True)

    with open(os.path.join(pasta, "benchmark.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    colunas = ["valor", "triangulos", "config", "cand_grade", "cand_envelope", "testes",
               "contem", "tempo_us", "speedup", "construcao_grade_ms", "indices_por_celula"]
    with open(os.path.join(pasta, "benchmark.md"), "w", encoding="utf-8") as f:
        f.write("# Resultados do benchmark\n\n")
        f.write("Base: %s. Valores sao medias por consulta.\n\n" % BASE)
        for fator, _ in FATORES:
            f.write("## Variando `%s`\n\n" % fator)
            f.write("| " + " | ".join(colunas) + " |\n")
            f.write("|" + "---|" * len(colunas) + "\n")
            for l in linhas:
                if l["fator"] == fator:
                    f.write("| " + " | ".join(Formata(l[c], 2 if c == "speedup" else 1)
                                              for c in colunas) + " |\n")
            f.write("\n")
    print("Gravado em", pasta)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rapido", action="store_true", help="menos pontos e repeticoes")
    inicio = time.perf_counter()
    Grava(Executa(parser.parse_args().rapido))
    print("Tempo total: %.1f s" % (time.perf_counter() - inicio))
