# Converte trabalho/RELATORIO.md em trabalho/RELATORIO.pdf (Markdown -> HTML -> Edge headless).
# Uso: python ferramentas/gera_pdf.py

import os
import pathlib
import subprocess
import tempfile

import markdown

TRABALHO = pathlib.Path(__file__).resolve().parent.parent / "trabalho"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h1 { font-size: 18pt; margin-bottom: 4pt; }
h2 { font-size: 14pt; border-bottom: 1px solid #bbb; padding-bottom: 2pt; margin-top: 18pt; }
h3 { font-size: 12pt; margin-top: 14pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.5pt; margin: 6pt 0; page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #eee; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f3f3f3; padding: 0 2pt; }
pre { background: #f3f3f3; padding: 6pt; font-size: 8pt; white-space: pre-wrap; }
pre code { background: none; padding: 0; }
img { display: block; max-width: 85%; margin: 8pt auto 2pt; border: 1px solid #ccc; }
p:has(> img) { page-break-inside: avoid; }
"""

texto = (TRABALHO / "RELATORIO.md").read_text(encoding="utf-8")
corpo = markdown.markdown(texto, extensions=["tables", "fenced_code"])
html = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<base href="%s/"><style>%s</style></head><body>%s</body></html>'
        % (TRABALHO.as_uri(), CSS, corpo))

with tempfile.TemporaryDirectory() as pasta:
    entrada = os.path.join(pasta, "relatorio.html")
    with open(entrada, "w", encoding="utf-8") as f:
        f.write(html)
    saida = TRABALHO / "RELATORIO.pdf"
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", "--print-to-pdf=%s" % saida,
                    pathlib.Path(entrada).as_uri()], check=True, timeout=120)

print("Gerado:", saida, "(%d KB)" % (saida.stat().st_size // 1024))
