import os
import tempfile
import requests
from pdf2image import convert_from_path

POPPLER_PATH = r"C:\poppler\Library\bin"

def baixar_pdf(url_pdf: str) -> str:
    response = requests.get(url_pdf)
    response.raise_for_status()
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_pdf.write(response.content)
    temp_pdf.close()
    return temp_pdf.name

def converter_pdf_para_png(caminho_pdf: str) -> list[str]:
    imagens = convert_from_path(caminho_pdf, dpi=200, poppler_path=POPPLER_PATH)
    caminhos_png = []
    for i, imagem in enumerate(imagens):
        caminho_png = os.path.join(tempfile.gettempdir(), f"pagina_{i+1}.png")
        imagem.save(caminho_png, "PNG")
        caminhos_png.append(caminho_png)
    return caminhos_png

def analisar_pdf_com_scout(url_pdf: str, pergunta: str = "Descreva essa imagem detalhadamente!") -> list[str]:
    caminho_pdf = baixar_pdf(url_pdf)
    imagens_png = converter_pdf_para_png(caminho_pdf)
    return imagens_png
