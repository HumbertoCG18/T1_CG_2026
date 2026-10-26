# ************************************************
#   Testes.py
#   Auto-verificacao: casos do enunciado (aresta/vertice) e igualdade
#   dos resultados das 4 configuracoes com a forca bruta.
#   Uso: python Testes.py
# ************************************************

import random

from Ponto import Ponto
from Triangulo import Triangulo
from Cenario import GeraAleatorio, LeArquivo, SalvaArquivo
from Consulta import Consulta, CONFIGURACOES


def TestaCasosDoEnunciado():
    T = Triangulo(Ponto(0, 0), Ponto(5, 0), Ponto(0, 5), 0)
    assert T.PontoNoTriangulo(Ponto(1, 1))           # dentro
    assert not T.PontoNoTriangulo(Ponto(5, 5))       # fora
    assert T.PontoNoTriangulo(Ponto(0, 2))           # sobre a aresta AC
    assert T.PontoNoTriangulo(Ponto(5, 0))           # sobre o vertice B
    assert T.PontoNoTriangulo(Ponto(2.5, 2.5))       # sobre a hipotenusa
    # A hipotenusa calculada em float pode ficar fora por arredondamento;
    # a tolerancia precisa aceitar o ponto.
    assert T.PontoNoTriangulo(Ponto(0.1 * 5, 5 - 0.1 * 5))
    assert not T.PontoNoTriangulo(Ponto(-1e-6, 2))   # fora, alem da tolerancia
    assert not T.PontoNoTriangulo(Ponto(2.5, 2.5 + 1e-6))


def PontosDeTeste(cenario, rng, n):
    # Pontos sorteados + vertices e pontos medios de arestas (casos de borda)
    pontos = [Ponto(rng.uniform(cenario.Min.x, cenario.Max.x),
                    rng.uniform(cenario.Min.y, cenario.Max.y)) for _ in range(n)]
    for T in rng.sample(cenario.Triangulos, min(50, len(cenario.Triangulos))):
        A, B, C = T.Vertices
        pontos += [A, B, C, Ponto((A.x + B.x) / 2, (A.y + B.y) / 2)]
    return pontos


def TestaConfiguracoesIguais():
    rng = random.Random(123)
    for n, tamanho, nx, ny in [(200, 1.0, 16, 8), (1000, 0.3, 40, 20), (300, 5.0, 3, 2), (50, 2.0, 1, 1)]:
        cenario = GeraAleatorio(n, semente=n, tamanho=tamanho)
        cenario.ConstroiGrade(nx, ny)
        for P in PontosDeTeste(cenario, rng, 500):
            referencia = Consulta(cenario, P, False, False).Contem
            for nome, usaGrade, usaEnvelope in CONFIGURACOES[1:]:
                r = Consulta(cenario, P, usaGrade, usaEnvelope)
                assert sorted(r.Contem) == sorted(referencia), (nome, n, P.x, P.y)
                assert r.Testes <= n


def TestaMesmaSemente():
    a = GeraAleatorio(100, semente=7, tamanho=1.0)
    b = GeraAleatorio(100, semente=7, tamanho=1.0)
    assert all(Ta.Vertices[i].x == Tb.Vertices[i].x and Ta.Vertices[i].y == Tb.Vertices[i].y
               for Ta, Tb in zip(a.Triangulos, b.Triangulos) for i in range(3))


def TestaArquivo():
    import os
    import tempfile
    a = GeraAleatorio(50, semente=3, tamanho=1.0)
    nome = os.path.join(tempfile.mkdtemp(), "cenario.txt")
    SalvaArquivo(a, nome)
    b = LeArquivo(nome)
    assert [(V.x, V.y) for T in a.Triangulos for V in T.Vertices] == \
           [(V.x, V.y) for T in b.Triangulos for V in T.Vertices]


def TestaEntradasInvalidas():
    import os
    import tempfile
    pasta = tempfile.mkdtemp()
    for conteudo in ["", "# so comentario\n", "1\n0 0 nan 1 1 0\n", "0\n", "2\n0 0 1 0 0 1\n", "x\n"]:
        nome = os.path.join(pasta, "ruim.txt")
        with open(nome, "w") as f:
            f.write(conteudo)
        try:
            LeArquivo(nome)
            assert False, "aceitou arquivo invalido: %r" % conteudo
        except ValueError:
            pass
    for n, tamanho in [(3, 0), (0, 1.0), (3, -1.0)]:
        try:
            GeraAleatorio(n, 1, tamanho)
            assert False, (n, tamanho)
        except ValueError:
            pass


def TestaContadores():
    cenario = GeraAleatorio(500, semente=5, tamanho=1.0)
    cenario.ConstroiGrade(16, 8)
    P = Ponto(0.3, 0.2)
    r = Consulta(cenario, P, True, True)
    assert r.Testes == len(r.CandEnvelope) <= len(r.CandGrade)
    assert Consulta(cenario, P, False, False).Testes == 500
    assert Consulta(cenario, Ponto(1e3, 1e3), True, False).Testes == 0   # fora da grade


if __name__ == "__main__":
    TestaEntradasInvalidas()
    TestaContadores()
    TestaCasosDoEnunciado()
    TestaMesmaSemente()
    TestaArquivo()
    TestaConfiguracoesIguais()
    print("OK: todos os testes passaram")
