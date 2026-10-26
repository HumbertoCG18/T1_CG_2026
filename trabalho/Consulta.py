# ************************************************
#   Consulta.py
#   Algoritmo de inclusao de ponto com ate tres etapas:
#       1) subdivisao espacial (grade)   -> opcional
#       2) teste com envelopes (AABB)    -> opcional
#       3) teste detalhado (orientacao)  -> sempre
#   As etapas 1 e 2 so reduzem o conjunto de candidatos; o resultado
#   final vem sempre do teste detalhado.
# ************************************************

import time


class Resultado:
    def __init__(self, total):
        self.Total = total            # triangulos no cenario
        self.Celula = None            # (ix, iy) da celula do ponto, se usou grade
        self.CandGrade = None         # indices vindos da grade (None = etapa desligada)
        self.CandEnvelope = None      # indices aprovados no envelope (None = etapa desligada)
        self.Testes = 0               # testes detalhados executados
        self.Contem = []              # indices dos triangulos que contem o ponto
        self.Tempo = 0.0              # segundos

    def Linha(self):
        def qtd(lista):
            return "-" if lista is None else str(len(lista))
        return ("total=%d grade=%s envelope=%s testes=%d contem=%d tempo=%.1fus"
                % (self.Total, qtd(self.CandGrade), qtd(self.CandEnvelope),
                   self.Testes, len(self.Contem), self.Tempo * 1e6))


# **********************************************************************
# Consulta(cenario, P, usaGrade, usaEnvelope)
#      Executa uma consulta e devolve um Resultado com os contadores
#      zerados para esta posicao do ponto.
# **********************************************************************
def Consulta(cenario, P, usaGrade, usaEnvelope):
    T = cenario.Triangulos
    r = Resultado(len(T))

    inicio = time.perf_counter()

    if usaGrade:
        r.Celula, candidatos = cenario.Grade.Candidatos(P)
        r.CandGrade = candidatos
    else:
        candidatos = range(len(T))

    if usaEnvelope:
        candidatos = [i for i in candidatos if T[i].PontoNoEnvelope(P)]
        r.CandEnvelope = candidatos

    r.Contem = [i for i in candidatos if T[i].PontoNoTriangulo(P)]
    r.Testes = len(candidatos)

    r.Tempo = time.perf_counter() - inicio
    return r


# Configuracoes exigidas pelo enunciado: (nome, usaGrade, usaEnvelope)
CONFIGURACOES = [
    ("forca bruta", False, False),
    ("envelope", False, True),
    ("grade", True, False),
    ("grade+envelope", True, True),
]
