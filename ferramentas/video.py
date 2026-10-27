# Gera o video de demonstracao (video/demo.mp4) seguindo os tempos do
# ROTEIRO_VIDEO.md. Roda o ProgramaT1.py sem modifica-lo: os eventos de teclado e
# mouse sao enviados aos proprios handlers do programa e cada quadro e lido do
# back buffer com glReadPixels. Abaixo da janela aparece o console do programa;
# a tecla pressionada e a etapa do roteiro aparecem sobre a imagem.
#
# Uso:   python ferramentas/video.py
# Audio: python ferramentas/video.py --audio narracao.wav   (junta ao video)

import argparse
import io
import os
import pathlib
import runpy
import subprocess
import sys

import fitz
import OpenGL.GLUT as GLUT
from OpenGL.GL import glGetIntegerv, glReadBuffer, glReadPixels, GL_VIEWPORT, GL_BACK, GL_RGB, GL_UNSIGNED_BYTE
from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TRABALHO = RAIZ / "trabalho"
SAIDA = RAIZ / "video"
FPS = 30
LARG, ALT, ALT_JANELA = 1000, 720, 600

parser = argparse.ArgumentParser()
parser.add_argument("--audio", help="arquivo de audio para juntar ao video ja gerado")
opcoes = parser.parse_args()
SAIDA.mkdir(exist_ok=True)

if opcoes.audio:
    subprocess.run(["ffmpeg", "-y", "-i", str(SAIDA / "demo.mp4"), "-i", opcoes.audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    str(SAIDA / "demo_com_audio.mp4")], check=True)
    sys.exit(0)

MONO = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 14)
MONO_G = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 20)
SANS = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18)

# Saida do Testes.py e pagina de resultados do relatorio, preparadas antes da janela abrir
saidaTestes = subprocess.run([sys.executable, "Testes.py"], cwd=TRABALHO,
                             capture_output=True, text=True).stdout.strip()
pdf = fitz.open(TRABALHO / "RELATORIO.pdf")
paginaPdf = next(p for p in pdf if p.search_for("6.2 Tamanho"))
zoom = LARG / paginaPdf.rect.width
pix = paginaPdf.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
imagemPdf = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
yPdf = int(paginaPdf.search_for("6.1 Quantidade")[0].y0 * zoom) if paginaPdf.search_for("6.1 Quantidade") else 0


# Console: guarda as linhas impressas pelo programa
class Console(io.TextIOBase):
    def __init__(self):
        self.linhas = []

    def write(self, s):
        self.linhas.extend(l for l in s.splitlines() if l.strip())
        return len(s)


console = Console()
sys.stdout = console

os.chdir(TRABALHO)
sys.path.insert(0, str(TRABALHO))
sys.argv = ["ProgramaT1.py", "--n", "150", "--tamanho", "1.2", "--semente", "1", "--grade", "16", "8"]

callbacks, quadro = {}, {}
_displayFunc, _swap = GLUT.glutDisplayFunc, GLUT.glutSwapBuffers


def displayFunc(f):
    callbacks["display"] = f
    _displayFunc(f)


def swap():
    _, _, w, h = glGetIntegerv(GL_VIEWPORT)
    glReadBuffer(GL_BACK)
    dados = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)
    quadro["img"] = Image.frombytes("RGB", (w, h), dados).transpose(Image.FLIP_TOP_BOTTOM)
    _swap()


def mainloop():
    g = callbacks["display"].__globals__
    for _ in range(30):
        GLUT.glutMainLoopEvent()
    # a ajuda impressa na abertura empurraria a linha da semente para fora do console
    console.linhas = [l for l in console.linhas if l.startswith(("Cenario", "Grade", "P="))]

    ffmpeg = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", "%dx%d" % (LARG, ALT), "-r", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                               str(SAIDA / "demo.mp4")], stdin=subprocess.PIPE)
    estado = dict(t=0, legenda="", tecla="", teclaAte=0, cursor=None)

    def Pixel(P):
        Min, Max = g["Min"], g["Max"]
        return (int((P.x - Min.x) / (Max.x - Min.x) * LARG),
                int((Max.y - P.y) / (Max.y - Min.y) * ALT_JANELA))

    def Compoe(fundo):
        img = Image.new("RGB", (LARG, ALT), "white")
        img.paste(fundo.resize((LARG, ALT_JANELA)) if fundo.size != (LARG, ALT_JANELA) else fundo, (0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle([0, ALT_JANELA, LARG, ALT], fill=(24, 24, 24))
        for k, linha in enumerate(console.linhas[-6:]):
            d.text((8, ALT_JANELA + 6 + 18 * k), linha[:130], font=MONO, fill=(220, 220, 220))
        if estado["cursor"]:
            x, y = estado["cursor"]
            d.polygon([(x, y), (x, y + 20), (x + 5, y + 15), (x + 9, y + 23), (x + 12, y + 21),
                       (x + 8, y + 14), (x + 15, y + 14)], fill="white", outline="black")
        if estado["legenda"]:
            w = d.textlength(estado["legenda"], font=SANS)
            d.rounded_rectangle([LARG - w - 28, ALT_JANELA - 44, LARG - 8, ALT_JANELA - 10], 8, fill=(20, 60, 140))
            d.text((LARG - w - 18, ALT_JANELA - 41), estado["legenda"], font=SANS, fill="white")
        if estado["tecla"] and estado["t"] < estado["teclaAte"]:
            texto = "tecla: " + estado["tecla"]
            w = d.textlength(texto, font=MONO_G)
            d.rounded_rectangle([LARG - w - 32, 170, LARG - 12, 210], 8, fill=(40, 40, 40))
            d.text((LARG - w - 22, 178), texto, font=MONO_G, fill="white")
        return img

    def Grava(img, segundos):
        for _ in range(max(1, round(segundos * FPS))):
            ffmpeg.stdin.write(Compoe(img).tobytes())
            estado["t"] += 1 / FPS

    def Programa(segundos):
        GLUT.glutMainLoopEvent()
        callbacks["display"]()
        Grava(quadro["img"], segundos)

    def Ate(instante):
        # Mantem a imagem atual ate o instante (s) do roteiro
        if instante > estado["t"]:
            Programa(instante - estado["t"])

    def Tecla(nome, chave, especial=False):
        estado["tecla"], estado["teclaAte"] = nome, estado["t"] + 1.5
        if especial:
            g["arrow_keys"](chave, 0, 0)
        else:
            g["keyboard"](chave, 0, 0)

    def Arrasta(P0, P1, segundos):
        Ponto = g["Ponto"]
        n = round(segundos * FPS)
        for k in range(n + 1):
            P = Ponto(P0.x + (P1.x - P0.x) * k / n, P0.y + (P1.y - P0.y) * k / n)
            x, y = Pixel(P)
            estado["cursor"] = (x, y)
            if k == 0:
                g["Mouse"](GLUT.GLUT_LEFT_BUTTON, GLUT.GLUT_DOWN, x, y)
            else:
                g["MouseArrasta"](x, y)
            Programa(1 / FPS)

    Ponto = g["Ponto"]
    alvo = Ponto(5.167, -1.167)

    # 0:00 cenario aleatorio com semente
    estado["legenda"] = "Cenário aleatório com semente 1"
    Ate(10)

    # 0:10 controle do ponto
    estado["legenda"] = "Controle do ponto: mouse e setas"
    Arrasta(Ponto(-6, 1), Ponto(-2, -2), 2.5)
    Arrasta(Ponto(-2, -2), Ponto(2, 2), 2.5)
    Arrasta(Ponto(2, 2), Ponto(4.5, -1.3), 2.5)
    estado["cursor"] = None
    for _ in range(4):
        Tecla("→", GLUT.GLUT_KEY_RIGHT, True)
        Programa(0.4)
    Tecla("↑", GLUT.GLUT_KEY_UP, True)
    Programa(0.4)
    g["PontoAtual"] = alvo
    g["AtualizaConsulta"]()
    Ate(22)

    # 0:22 categorias e toggles de visualizacao
    estado["legenda"] = "Célula · candidatos grade · envelope · contém"
    Ate(29)
    for instante, nome in [(29, "b"), (33, "b"), (36, "g"), (38.5, "g"), (41, "c"), (43.5, "c")]:
        Ate(instante)
        Tecla(nome + "  (visualização)", nome.encode())
    Ate(45)

    # 0:45 as quatro configuracoes
    estado["legenda"] = "As 4 configurações: mesmo resultado"
    for instante, nome in [(45, "1"), (51, "2"), (57, "3"), (63, "4")]:
        Ate(instante)
        Tecla(nome, nome.encode())
    Ate(68)

    # 1:08 resolucao da grade
    estado["legenda"] = "Parametrização da grade"
    for instante, nome in [(69, "+"), (72, "+"), (76, "-"), (78, "-")]:
        Ate(instante)
        Tecla(nome, nome.encode())
    Ate(80)

    # 1:20 cenario grande
    estado["legenda"] = "20.000 triângulos"
    A = g["Args"]
    A.n, A.tamanho, A.semente, A.arquivo, A.grade = 20000, 0.3, 1, None, [64, 32]
    g["CriaCenario"]()
    g["PontoAtual"] = Ponto(0.3, 0.2)
    g["AtualizaConsulta"]()
    Ate(82)
    Tecla("1", b"1")
    Ate(90)
    Tecla("4", b"4")
    Ate(98)

    # 1:38 testes automaticos
    estado["legenda"] = "Testes automáticos"
    terminal = Image.new("RGB", (LARG, ALT_JANELA), (12, 12, 12))
    d = ImageDraw.Draw(terminal)
    d.text((24, 24), "> python Testes.py", font=MONO_G, fill=(120, 220, 120))
    Grava(terminal, 2)
    d.text((24, 56), saidaTestes, font=MONO_G, fill="white")
    Grava(terminal, 110 - estado["t"])

    # 1:50 relatorio
    estado["legenda"] = "Relatório: comparação das configurações"
    n = round((120 - estado["t"]) * FPS)
    for k in range(n):
        y = min(yPdf + int(k * 1.2), imagemPdf.height - ALT_JANELA)
        Grava(imagemPdf.crop((0, y, LARG, y + ALT_JANELA)), 1 / FPS)

    ffmpeg.stdin.close()
    ffmpeg.wait()
    sys.stdout = sys.__stdout__
    print("Gerado:", SAIDA / "demo.mp4", "(%.1f s)" % estado["t"])
    os._exit(0)


GLUT.glutDisplayFunc = displayFunc
GLUT.glutSwapBuffers = swap
GLUT.glutMainLoop = mainloop
runpy.run_path("ProgramaT1.py", run_name="__main__")
