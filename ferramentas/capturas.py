# Gera as capturas de tela do relatorio rodando o ProgramaT1.py sem modifica-lo:
# substitui glutMainLoop por uma sequencia de estados e le o back buffer com
# glReadPixels antes de cada glutSwapBuffers.
# Uso: python ferramentas/capturas.py   (abre uma janela por alguns segundos)

import os
import runpy
import sys

import OpenGL.GLUT as GLUT
from OpenGL.GL import glGetIntegerv, glReadBuffer, glReadPixels, GL_VIEWPORT, GL_BACK, GL_RGB, GL_UNSIGNED_BYTE
from PIL import Image

TRABALHO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "trabalho")
SAIDA = os.path.join(TRABALHO, "imagens")
os.makedirs(SAIDA, exist_ok=True)
os.chdir(TRABALHO)
sys.path.insert(0, TRABALHO)
sys.argv = ["ProgramaT1.py", "--n", "150", "--tamanho", "1.2", "--semente", "1", "--grade", "16", "8"]

callbacks = {}
quadro = {}

_displayFunc = GLUT.glutDisplayFunc
_swap = GLUT.glutSwapBuffers


def displayFunc(f):
    callbacks["display"] = f
    _displayFunc(f)


def swap():
    _, _, w, h = glGetIntegerv(GL_VIEWPORT)
    glReadBuffer(GL_BACK)
    dados = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)
    quadro["img"] = Image.frombytes("RGB", (w, h), dados).transpose(Image.FLIP_TOP_BOTTOM)
    _swap()


def PontoComMaisTriangulos(g):
    # Varre a parte central de baixo (longe do painel de texto e das bordas)
    # e devolve o ponto em que as tres categorias aparecem: candidatos so da
    # grade, aprovados so no envelope e triangulos que contem o ponto.
    Cena, Ponto, Consulta = g["Cena"], g["Ponto"], g["Consulta"]
    Min, Max = Cena.Min, Cena.Max
    W, H = Max.x - Min.x, Max.y - Min.y
    melhor, nota = None, None
    for i in range(18, 103):
        for j in range(6, 27):
            P = Ponto(Min.x + W * i / 120, Min.y + H * j / 60)
            r = Consulta(Cena, P, True, True)
            contem, env, grade = len(r.Contem), len(r.CandEnvelope), len(r.CandGrade)
            n = (min(env - contem, 1), min(grade - env, 1), min(contem, 3), min(grade - env, 4))
            if nota is None or n > nota:
                melhor, nota = P, n
    return melhor


def mainloop():
    g = callbacks["display"].__globals__
    for _ in range(30):
        GLUT.glutMainLoopEvent()

    def captura(nome, **estado):
        g.update(estado)
        g["AtualizaConsulta"]()
        callbacks["display"]()
        quadro["img"].save(os.path.join(SAIDA, nome + ".png"))
        print("   ->", nome + ".png")

    P = PontoComMaisTriangulos(g)
    base = dict(PontoAtual=P, MostraGrade=True, MostraCandidatos=True, MostraEnvelopes=False)

    captura("01_grade_envelope", UsaGrade=True, UsaEnvelope=True, **base)
    captura("02_so_grade", UsaGrade=True, UsaEnvelope=False, **base)
    captura("03_envelopes", UsaGrade=False, UsaEnvelope=True,
            **dict(base, MostraGrade=False, MostraEnvelopes=True))
    captura("04_forca_bruta", UsaGrade=False, UsaEnvelope=False, **dict(base, MostraGrade=False))

    g["Args"].grade = [64, 32]
    g["Cena"].ConstroiGrade(64, 32)
    captura("05_grade_64x32", UsaGrade=True, UsaEnvelope=True, **base)

    g["Args"].arquivo = "cenarios/exemplo.txt"
    g["Args"].grade = [4, 2]
    g["CriaCenario"]()
    captura("06_vertice_compartilhado", UsaGrade=True, UsaEnvelope=True,
            **dict(base, PontoAtual=g["Ponto"](5, 0)))
    os._exit(0)


GLUT.glutDisplayFunc = displayFunc
GLUT.glutSwapBuffers = swap
GLUT.glutMainLoop = mainloop
runpy.run_path("ProgramaT1.py", run_name="__main__")
