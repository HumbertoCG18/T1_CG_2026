# **********************************************************************
# PUCRS/Escola Politecnica
# COMPUTACAO GRAFICA - Trabalho I 2026/2
# Inclusao de ponto em poligonos com aceleracao
#
# Visualizacao em OpenGL/GLUT, baseada no Prog-Triangulos.py do
# Prof. Marcio Sarroglia Pinho.
#
# Uso:
#   python ProgramaT1.py [--n 1000] [--semente 1] [--tamanho 1.0]
#                        [--arquivo cenarios/exemplo.txt] [--grade 16 8]
#
# Teclas (tambem impressas com 'h'):
#   s/e        liga/desliga etapa de subdivisao (grade) / envelopes
#   1..4       configuracoes: 1 forca bruta, 2 envelope, 3 grade, 4 grade+envelope
#   g/b/c      mostra/esconde grade, envelopes, candidatos intermediarios
#   + / -      dobra / divide a resolucao da grade (reconstroi)
#   r          novo cenario aleatorio com a proxima semente
#   w          salva o cenario corrente em cenarios/
#   setas      movem o ponto; clique/arraste com o botao esquerdo posiciona
#   q / ESC    sai
# **********************************************************************

import argparse
import os
import sys

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from Ponto import Ponto
import Cenario
from Consulta import Consulta, CONFIGURACOES

# Cores RGBA de cada categoria (alpha permite ver sobreposicoes)
COR_GRADE = (0.80, 0.80, 0.80, 1.0)
COR_CELULA = (1.00, 0.95, 0.55, 1.0)
COR_ENVELOPE = (0.55, 0.35, 0.80, 0.6)
COR_CAND_GRADE = (0.30, 0.55, 1.00, 0.25)
COR_CAND_ENVELOPE = (1.00, 0.60, 0.10, 0.40)
COR_CONTEM = (0.85, 0.05, 0.10, 0.65)
COR_ARESTA = (0.35, 0.35, 0.35, 1.0)

# Estado da aplicacao
Args = None
Cena = None
Min = Ponto()
Max = Ponto()
PontoAtual = Ponto()
Res = None

UsaGrade = True
UsaEnvelope = True
MostraGrade = True
MostraEnvelopes = False
MostraCandidatos = True

ListaArestas = None
ListaEnvelopes = None
LarguraJanela, AlturaJanela = 1000, 600


# **********************************************************************
# CriaCenario()
#      Cria (ou le) o cenario conforme os argumentos e constroi a grade.
# **********************************************************************
def CriaCenario():
    global Cena, Min, Max, PontoAtual

    if Args.arquivo:
        Cena = Cenario.LeArquivo(Args.arquivo)
    else:
        Cena = Cenario.GeraAleatorio(Args.n, Args.semente, Args.tamanho)

    Cena.ConstroiGrade(Args.grade[0], Args.grade[1])
    Min, Max = Cena.Min, Cena.Max
    PontoAtual = Ponto((Min.x + Max.x) / 2, (Min.y + Max.y) / 2)

    print("Cenario: %s, %d triangulos" % (Cena.Descricao(), len(Cena.Triangulos)))
    ImprimeGrade()
    CompilaListas()
    reshape(LarguraJanela, AlturaJanela)
    AtualizaConsulta()


def ImprimeGrade():
    media, maximo, total = Cena.Grade.Estatisticas()
    print("Grade %dx%d construida em %.2f ms: %.1f indices/celula (max %d, total %d)"
          % (Cena.Grade.nx, Cena.Grade.ny, Cena.TempoGrade * 1e3, media, maximo, total))


# **********************************************************************
# CompilaListas()
#      Triangulos sao estaticos: arestas e envelopes vao para display
#      lists, compiladas uma vez por cenario, para desenhar rapido.
# **********************************************************************
def CompilaListas():
    global ListaArestas, ListaEnvelopes

    if ListaArestas is None:
        ListaArestas = glGenLists(2)
        ListaEnvelopes = ListaArestas + 1

    glNewList(ListaArestas, GL_COMPILE)
    glBegin(GL_LINES)
    for T in Cena.Triangulos:
        V = T.Vertices
        for i in range(3):
            glVertex2f(V[i].x, V[i].y)
            glVertex2f(V[(i + 1) % 3].x, V[(i + 1) % 3].y)
    glEnd()
    glEndList()

    glNewList(ListaEnvelopes, GL_COMPILE)
    for T in Cena.Triangulos:
        T.DesenhaEnvelope()
    glEndList()


# **********************************************************************
# AtualizaConsulta()
#      Refaz a consulta para a posicao corrente do ponto. Chamada apos
#      qualquer movimento do ponto ou mudanca de etapa/cenario.
# **********************************************************************
def AtualizaConsulta():
    global Res
    Res = Consulta(Cena, PontoAtual, UsaGrade, UsaEnvelope)
    print("P=(%.3f, %.3f) [%s] %s" % (PontoAtual.x, PontoAtual.y, NomeConfiguracao(), Res.Linha()))
    glutPostRedisplay()


def NomeConfiguracao():
    for nome, g, e in CONFIGURACOES:
        if (g, e) == (UsaGrade, UsaEnvelope):
            return nome


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    CriaCenario()


# **********************************************************************
# reshape(w, h)
#      Trata o redimensionamento da janela OpenGL.
# **********************************************************************
def reshape(w, h):
    global LarguraJanela, AlturaJanela
    LarguraJanela, AlturaJanela = w, max(h, 1)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, w, h)
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


# **********************************************************************
# Rotinas de desenho de cada categoria
# **********************************************************************
def Retangulo(P0, P1, modo):
    glBegin(modo)
    glVertex2f(P0.x, P0.y)
    glVertex2f(P1.x, P0.y)
    glVertex2f(P1.x, P1.y)
    glVertex2f(P0.x, P1.y)
    glEnd()


def DesenhaGrade():
    G = Cena.Grade
    glColor4f(*COR_GRADE)
    glBegin(GL_LINES)
    for ix in range(G.nx + 1):
        x = G.Min.x + ix * G.dx
        glVertex2f(x, G.Min.y)
        glVertex2f(x, G.Max.y)
    for iy in range(G.ny + 1):
        y = G.Min.y + iy * G.dy
        glVertex2f(G.Min.x, y)
        glVertex2f(G.Max.x, y)
    glEnd()


def DesenhaCelulaDoPonto():
    celula = Cena.Grade.CelulaDoPonto(PontoAtual)
    if celula is not None:
        glColor4f(*COR_CELULA)
        Retangulo(*Cena.Grade.LimitesDaCelula(*celula), GL_QUADS)


def PintaTriangulos(indices, cor):
    glColor4f(*cor)
    glBegin(GL_TRIANGLES)
    for i in indices:
        for V in Cena.Triangulos[i].Vertices:
            glVertex2f(V.x, V.y)
    glEnd()


def DesenhaPonto():
    glPointSize(9)
    glColor3f(0, 0, 0)
    glBegin(GL_POINTS)
    glVertex2f(PontoAtual.x, PontoAtual.y)
    glEnd()
    glPointSize(5)
    glColor3f(1, 1, 1)
    glBegin(GL_POINTS)
    glVertex2f(PontoAtual.x, PontoAtual.y)
    glEnd()
    glPointSize(1)


# **********************************************************************
# DesenhaPainel()
#      Escreve contadores e legenda em coordenadas de pixel.
# **********************************************************************
def Texto(x, y, s, cor=(0, 0, 0)):
    glColor3f(*cor)
    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))


def DesenhaPainel():
    def qtd(lista):
        return "-" if lista is None else str(len(lista))

    G = Cena.Grade
    linhas = [
        ("Config: %s   [s] grade %s  [e] envelope %s" % (NomeConfiguracao(),
            "ON" if UsaGrade else "off", "ON" if UsaEnvelope else "off"), (0, 0, 0)),
        ("Ponto: (%.3f, %.3f)" % (PontoAtual.x, PontoAtual.y), (0, 0, 0)),
        ("Triangulos: %d   Grade %dx%d (%.1f ms)" % (Res.Total, G.nx, G.ny, Cena.TempoGrade * 1e3), (0, 0, 0)),
        ("Candidatos grade: %s" % qtd(Res.CandGrade), COR_CAND_GRADE[:3]),
        ("Aprovados envelope: %s" % qtd(Res.CandEnvelope), COR_CAND_ENVELOPE[:3]),
        ("Testes detalhados: %d" % Res.Testes, (0, 0, 0)),
        ("Contem o ponto: %d" % len(Res.Contem), COR_CONTEM[:3]),
        ("Tempo da consulta: %.1f us" % (Res.Tempo * 1e6), (0, 0, 0)),
        ("[g] grade  [b] envelopes  [c] candidatos  [+/-] resolucao  [h] ajuda", (0.3, 0.3, 0.3)),
    ]

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, LarguraJanela, 0, AlturaJanela)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    altura = 17 * len(linhas) + 8
    glColor4f(1, 1, 1, 0.85)
    Retangulo(Ponto(0, AlturaJanela - altura), Ponto(620, AlturaJanela), GL_QUADS)
    for k, (s, cor) in enumerate(linhas):
        Texto(8, AlturaJanela - 17 * (k + 1), s, cor)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# **********************************************************************
# display()
#      Ordem: grade, celula do ponto, candidatos (grade -> envelope),
#      triangulos que contem o ponto, arestas, envelopes, ponto, painel.
#      A visualizacao so le Res; nao altera o resultado da consulta.
# **********************************************************************
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if MostraGrade:
        DesenhaCelulaDoPonto()
        DesenhaGrade()

    if MostraCandidatos:
        if Res.CandGrade is not None:
            PintaTriangulos(Res.CandGrade, COR_CAND_GRADE)
        if Res.CandEnvelope is not None:
            PintaTriangulos(Res.CandEnvelope, COR_CAND_ENVELOPE)

    PintaTriangulos(Res.Contem, COR_CONTEM)

    glColor4f(*COR_ARESTA)
    glCallList(ListaArestas)

    if MostraEnvelopes:
        glColor4f(*COR_ENVELOPE)
        glCallList(ListaEnvelopes)

    DesenhaPonto()
    DesenhaPainel()

    glutSwapBuffers()


# **********************************************************************
# ConverteMouseParaUniverso(x, y)
#      Converte as coordenadas do mouse para as coordenadas do universo.
# **********************************************************************
def ConverteMouseParaUniverso(x, y):
    viewport = glGetIntegerv(GL_VIEWPORT)

    vx = viewport[0]
    vy = viewport[1]
    largura = viewport[2]
    altura = viewport[3]

    ux = Min.x + ((x - vx) / largura) * (Max.x - Min.x)
    uy = Max.y - ((y - vy) / altura) * (Max.y - Min.y)

    return Ponto(ux, uy, 0)


def Mouse(button, state, x, y):
    global PontoAtual
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        PontoAtual = ConverteMouseParaUniverso(x, y)
        AtualizaConsulta()


def MouseArrasta(x, y):
    global PontoAtual
    PontoAtual = ConverteMouseParaUniverso(x, y)
    AtualizaConsulta()


def ImprimeAjuda():
    with open(__file__, encoding="utf-8") as f:
        for linha in f:
            if linha.startswith("# Teclas"):
                break
        for linha in f:
            if linha.startswith("# ****"):
                break
            print(linha.rstrip()[2:])


ESCAPE = b'\x1b'
def keyboard(key, x, y):
    global UsaGrade, UsaEnvelope, MostraGrade, MostraEnvelopes, MostraCandidatos

    if key in (b'q', ESCAPE):
        os._exit(0)
    elif key == b's':
        UsaGrade = not UsaGrade
    elif key == b'e':
        UsaEnvelope = not UsaEnvelope
    elif key in (b'1', b'2', b'3', b'4'):
        _, UsaGrade, UsaEnvelope = CONFIGURACOES[int(key) - 1]
    elif key == b'g':
        MostraGrade = not MostraGrade
    elif key == b'b':
        MostraEnvelopes = not MostraEnvelopes
    elif key == b'c':
        MostraCandidatos = not MostraCandidatos
    elif key in (b'+', b'=', b'-'):
        fator = 0.5 if key == b'-' else 2
        Args.grade = [max(1, int(Args.grade[0] * fator)), max(1, int(Args.grade[1] * fator))]
        Cena.ConstroiGrade(*Args.grade)
        ImprimeGrade()
    elif key == b'r':
        Args.arquivo = None
        Args.semente += 1
        CriaCenario()
        return
    elif key == b'w':
        nome = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cenarios",
                            "cenario_%d_tri.txt" % len(Cena.Triangulos))
        Cenario.SalvaArquivo(Cena, nome)
        print("Cenario salvo em", nome)
        return
    elif key == b'h':
        ImprimeAjuda()
        return
    else:
        return

    AtualizaConsulta()


def arrow_keys(a_keys, x, y):
    global PontoAtual
    passo = (Max.x - Min.x) / 200
    dx, dy = {GLUT_KEY_UP: (0, passo), GLUT_KEY_DOWN: (0, -passo),
              GLUT_KEY_LEFT: (-passo, 0), GLUT_KEY_RIGHT: (passo, 0)}.get(a_keys, (0, 0))
    if dx or dy:
        PontoAtual = Ponto(PontoAtual.x + dx, PontoAtual.y + dy)
        AtualizaConsulta()


# **********************************************************************
# main()
# **********************************************************************
parser = argparse.ArgumentParser(description="T1 CG - inclusao de ponto em triangulos")
parser.add_argument("--n", type=int, default=1000, help="quantidade de triangulos aleatorios")
parser.add_argument("--semente", type=int, default=1, help="semente do gerador aleatorio")
parser.add_argument("--tamanho", type=float, default=1.0, help="meio-lado do quadrado onde os vertices sao sorteados")
parser.add_argument("--arquivo", help="le os triangulos deste arquivo em vez de gerar")
parser.add_argument("--grade", type=int, nargs=2, default=[16, 8], metavar=("NX", "NY"))
Args, _ = parser.parse_known_args()

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(LarguraJanela, AlturaJanela)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow(b"Trabalho 1 - Inclusao de ponto com aceleracao")

init()
ImprimeAjuda()

glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)
glutMouseFunc(Mouse)
glutMotionFunc(MouseArrasta)

try:
    glutMainLoop()
except SystemExit:
    pass
