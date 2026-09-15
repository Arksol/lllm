from app.rag.chunker import chunk_file

CODIGO = '''import os

def saludar(nombre):
    return f"hola {nombre}"

class Motor:
    def arrancar(self):
        return True
'''


def test_python_se_parte_por_simbolos_completos():
    chunks = chunk_file("app/motor.py", CODIGO)
    simbolos = {c.symbol for c in chunks}
    assert "saludar" in simbolos
    assert "Motor" in simbolos


def test_ningun_fragmento_corta_una_funcion():
    chunk = next(c for c in chunk_file("m.py", CODIGO) if c.symbol == "saludar")
    assert "def saludar" in chunk.text
    assert "return" in chunk.text


def test_el_titulo_identifica_archivo_y_lineas():
    chunk = chunk_file("m.py", CODIGO)[0]
    assert chunk.title.startswith("m.py#L")


def test_lenguaje_sin_parser_se_parte_por_lineas():
    chunks = chunk_file("app.js", "const a = 1;\n" * 300)
    assert len(chunks) > 1
    assert all(c.file_path == "app.js" for c in chunks)
