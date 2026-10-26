# ************************************************
#   Triangulo.py
#   Define a classe Triangulo
#   Autor: Marcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************


from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Ponto import *

from Ponto import Ponto
from ListaDeCoresRGB import defineCor

import math

# Tolerancia, em unidades do universo, para considerar um ponto sobre
# uma aresta ou vertice como pertencente ao triangulo.
EPSILON = 1e-9

# Margem dos envelopes e da grade. Precisa ser maior que o quanto a
# tolerancia "infla" o triangulo perto de vertices agudos
# (~2*EPSILON/Qualidade, ver QUALIDADE_MINIMA em Cenario.py).
MARGEM_ENVELOPE = 1e-5


""" Classe Triangulo """
class Triangulo:
    def __init__(self, *args):
        self.Vertices = [Ponto(), Ponto(), Ponto()]
        self.Envelope = [Ponto(), Ponto()]
        self.cor = 0

        # Construtor que recebe somente a cor
        if len(args) == 1:
            self.cor = args[0]

        # Construtor que recebe um vetor de vertices e a cor
        elif len(args) == 2:
            V, cor = args
            for i in range(3):
                self.Vertices[i] = Ponto(V[i].x, V[i].y, V[i].z)
            self.cor = cor

        # Construtor que recebe tres pontos e a cor
        elif len(args) == 4:
            P1, P2, P3, cor = args
            self.Vertices[0] = Ponto(P1.x, P1.y, P1.z)
            self.Vertices[1] = Ponto(P2.x, P2.y, P2.z)
            self.Vertices[2] = Ponto(P3.x, P3.y, P3.z)
            self.cor = cor

        else:
            raise TypeError("Parametros invalidos para o construtor de Triangulo")

        self.CalculaEnvelope()
        self.CalculaTolerancias()

    # **********************************************************************
    # CalculaTolerancias()
    #      Pre-calcula o comprimento das arestas (V0V1, V1V2, V2V0) e a
    #      tolerancia usada em PontoNoTriangulo para cada uma delas.
    # **********************************************************************
    def CalculaTolerancias(self):
        V = self.Vertices
        self.Comprimentos = [math.hypot(V[i].x - V[(i + 1) % 3].x, V[i].y - V[(i + 1) % 3].y)
                             for i in range(3)]
        self.Tol = [EPSILON * c for c in self.Comprimentos]

    # **********************************************************************
    # CalculaEnvelope()
    #      Calcula o envelope (AABB) do triangulo.
    #      Envelope[0] = ponto minimo e Envelope[1] = ponto maximo.
    # **********************************************************************
    def CalculaEnvelope(self):
        self.Envelope[0] = self.Vertices[0]
        self.Envelope[1] = self.Vertices[0]

        for i in range(1, 3):
            self.Envelope[0] = ObtemMinimo(self.Envelope[0], self.Vertices[i])
            self.Envelope[1] = ObtemMaximo(self.Envelope[1], self.Vertices[i])
    # **********************************************************************
    # setCor(C)
    #      Define a cor do triangulo.
    # **********************************************************************
    def setCor(self, C):
        self.cor = C

    # **********************************************************************
    # getCor()
    #      Retorna a cor do triangulo.
    # **********************************************************************
    def getCor(self):
        return self.cor

    # **********************************************************************
    # Pinta(cor=None)
    #      Desenha o triangulo preenchido.
    #      Se uma cor for informada, usa esta cor somente neste desenho.
    # **********************************************************************
    def Pinta(self, cor=None):
        if cor is None:
            cor = self.cor

        defineCor(cor)

        glBegin(GL_TRIANGLES)
        glVertex2f(self.Vertices[0].x, self.Vertices[0].y)
        glVertex2f(self.Vertices[1].x, self.Vertices[1].y)
        glVertex2f(self.Vertices[2].x, self.Vertices[2].y)
        glEnd()

    # **********************************************************************
    # Desenha(cor=None)
    #      Desenha as arestas do triangulo.
    #      Se uma cor for informada, usa esta cor somente neste desenho.
    # **********************************************************************
    def Desenha(self, cor=None):
        if cor is None:
            cor = self.cor

        defineCor(cor)

        glBegin(GL_LINE_LOOP)
        glVertex2f(self.Vertices[0].x, self.Vertices[0].y)
        glVertex2f(self.Vertices[1].x, self.Vertices[1].y)
        glVertex2f(self.Vertices[2].x, self.Vertices[2].y)
        glEnd()

    # **********************************************************************
    # DesenhaEnvelope()
    #      Desenha o envelope (AABB) do triangulo.
    # **********************************************************************
    def DesenhaEnvelope(self):
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.Envelope[0].x, self.Envelope[0].y)
        glVertex2f(self.Envelope[1].x, self.Envelope[0].y)
        glVertex2f(self.Envelope[1].x, self.Envelope[1].y)
        glVertex2f(self.Envelope[0].x, self.Envelope[1].y)
        glEnd()

    # **********************************************************************
    # getVertices(i=None)
    #      Sem parametro, retorna todos os vertices do triangulo.
    #      Com um indice, retorna somente o vertice indicado.
    # **********************************************************************
    def getVertices(self, i=None):
        if i is None:
            return self.Vertices

        if i >= 0 and i < 3:
            return self.Vertices[i]

        return Ponto()

    # **********************************************************************
    # imprime()
    #      Imprime as coordenadas dos vertices do triangulo.
    # **********************************************************************
    def imprime(self):
        print("[", end="")

        for i in range(3):
            print("(", self.Vertices[i].x, ", ",
                  self.Vertices[i].y, ")", sep="", end="")

            if i < 2:
                print(" - ", end="")

        print("]")

    # **********************************************************************
    # PontoNoTriangulo(P)
    #      Verifica se o ponto P esta dentro do triangulo.
    #      Pontos sobre as arestas ou vertices sao considerados internos.
    # **********************************************************************
    def PontoNoTriangulo(self, P):
        # Calcula a orientacao de P em relacao a cada aresta
        d1 = (P.x - self.Vertices[1].x) * (self.Vertices[0].y - self.Vertices[1].y) - \
             (self.Vertices[0].x - self.Vertices[1].x) * (P.y - self.Vertices[1].y)

        d2 = (P.x - self.Vertices[2].x) * (self.Vertices[1].y - self.Vertices[2].y) - \
             (self.Vertices[1].x - self.Vertices[2].x) * (P.y - self.Vertices[2].y)

        d3 = (P.x - self.Vertices[0].x) * (self.Vertices[2].y - self.Vertices[0].y) - \
             (self.Vertices[2].x - self.Vertices[0].x) * (P.y - self.Vertices[0].y)

        # Cada d vale (comprimento da aresta) * (distancia de P a reta da aresta).
        # Comparar com Tol[i] = EPSILON * comprimento equivale a uma tolerancia
        # de EPSILON em distancia, independente do tamanho do triangulo.
        t1, t2, t3 = self.Tol

        # Verifica se existem orientacoes com sinais diferentes
        temNegativo = (d1 < -t1) or (d2 < -t2) or (d3 < -t3)
        temPositivo = (d1 > t1) or (d2 > t2) or (d3 > t3)

        return not (temNegativo and temPositivo)

    # **********************************************************************
    # PontoNoEnvelope(P)
    #      Verifica se o ponto P esta dentro do envelope (AABB) do triangulo.
    #      Usa a margem MARGEM_ENVELOPE para nunca descartar um ponto que o
    #      teste detalhado (com tolerancia) consideraria interno.
    # **********************************************************************
    def PontoNoEnvelope(self, P):
        return (self.Envelope[0].x - MARGEM_ENVELOPE <= P.x <= self.Envelope[1].x + MARGEM_ENVELOPE and
                self.Envelope[0].y - MARGEM_ENVELOPE <= P.y <= self.Envelope[1].y + MARGEM_ENVELOPE)

    # **********************************************************************
    # Qualidade()
    #      Retorna (menor altura) / (maior aresta). Vale 0 para triangulos
    #      degenerados (vertices colineares) e ~0.87 para o equilatero.
    # **********************************************************************
    def Qualidade(self):
        maior = max(self.Comprimentos)
        if maior == 0:
            return 0.0
        A, B, C = self.Vertices
        dobroArea = abs((B.x - A.x) * (C.y - A.y) - (C.x - A.x) * (B.y - A.y))
        return dobroArea / (maior * maior)
