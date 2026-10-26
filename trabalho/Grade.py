# ************************************************
#   Grade.py
#   Subdivisao espacial por grade regular (uniforme).
#   Cada celula guarda somente os INDICES dos triangulos cujo envelope
#   (com margem) toca a celula; a geometria fica nos objetos Triangulo.
# ************************************************

from Ponto import Ponto
from Triangulo import MARGEM_ENVELOPE


class Grade:
    # **********************************************************************
    # Grade(triangulos, nx, ny)
    #      Constroi uma grade de nx por ny celulas que cobre os envelopes
    #      de todos os triangulos.
    # **********************************************************************
    def __init__(self, triangulos, nx, ny):
        self.nx = max(1, int(nx))
        self.ny = max(1, int(ny))

        # Limites da grade = uniao dos envelopes, inflada pela margem
        self.Min = Ponto(min(T.Envelope[0].x for T in triangulos) - MARGEM_ENVELOPE,
                         min(T.Envelope[0].y for T in triangulos) - MARGEM_ENVELOPE)
        self.Max = Ponto(max(T.Envelope[1].x for T in triangulos) + MARGEM_ENVELOPE,
                         max(T.Envelope[1].y for T in triangulos) + MARGEM_ENVELOPE)

        self.dx = (self.Max.x - self.Min.x) / self.nx
        self.dy = (self.Max.y - self.Min.y) / self.ny

        self.Celulas = [[] for _ in range(self.nx * self.ny)]

        for i, T in enumerate(triangulos):
            ix0, iy0 = self.IndiceDaCelula(T.Envelope[0].x - MARGEM_ENVELOPE,
                                           T.Envelope[0].y - MARGEM_ENVELOPE)
            ix1, iy1 = self.IndiceDaCelula(T.Envelope[1].x + MARGEM_ENVELOPE,
                                           T.Envelope[1].y + MARGEM_ENVELOPE)
            for iy in range(iy0, iy1 + 1):
                for ix in range(ix0, ix1 + 1):
                    self.Celulas[iy * self.nx + ix].append(i)

    # **********************************************************************
    # IndiceDaCelula(x, y)
    #      Retorna (ix, iy) da celula que contem (x, y), limitado a grade.
    #      Usado tanto na construcao quanto na consulta, para que pontos
    #      sobre a fronteira de celulas caiam sempre na mesma celula.
    # **********************************************************************
    def IndiceDaCelula(self, x, y):
        ix = int((x - self.Min.x) / self.dx)
        iy = int((y - self.Min.y) / self.dy)
        return min(max(ix, 0), self.nx - 1), min(max(iy, 0), self.ny - 1)

    # **********************************************************************
    # CelulaDoPonto(P)
    #      Retorna (ix, iy) da celula que contem P, ou None se P esta fora
    #      da grade (e, portanto, fora de todos os triangulos).
    # **********************************************************************
    def CelulaDoPonto(self, P):
        if not (self.Min.x <= P.x <= self.Max.x and self.Min.y <= P.y <= self.Max.y):
            return None
        return self.IndiceDaCelula(P.x, P.y)

    # **********************************************************************
    # Candidatos(P)
    #      Retorna (celula, lista de indices) dos triangulos candidatos.
    # **********************************************************************
    def Candidatos(self, P):
        celula = self.CelulaDoPonto(P)
        if celula is None:
            return None, []
        ix, iy = celula
        return celula, self.Celulas[iy * self.nx + ix]

    # **********************************************************************
    # LimitesDaCelula(ix, iy)
    #      Retorna os pontos minimo e maximo da celula, para desenho.
    # **********************************************************************
    def LimitesDaCelula(self, ix, iy):
        x0 = self.Min.x + ix * self.dx
        y0 = self.Min.y + iy * self.dy
        return Ponto(x0, y0), Ponto(x0 + self.dx, y0 + self.dy)

    # **********************************************************************
    # Estatisticas()
    #      Media e maximo de indices por celula, e total de indices
    #      (um triangulo grande aparece em varias celulas).
    # **********************************************************************
    def Estatisticas(self):
        tamanhos = [len(c) for c in self.Celulas]
        total = sum(tamanhos)
        return total / len(tamanhos), max(tamanhos), total
