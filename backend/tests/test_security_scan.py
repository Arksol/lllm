from app.repos.schemas import RepoFile
from app.security_scan.scanner import scan
from app.security_scan.schemas import Severity


def _reglas(texto: str, path: str = "app.py") -> set[str]:
    return {f.rule for f in scan([RepoFile(path=path, text=texto)])}


def test_detecta_credencial_en_codigo():
    assert "secreto-en-codigo" in _reglas('API_KEY = "sk-abcdefghijklmnop1234"')


def test_detecta_shell_sin_aislar():
    assert "shell-sin-aislar" in _reglas("subprocess.run(cmd, shell=True)")


def test_detecta_cors_abierto():
    assert "cors-abierto" in _reglas('allow_origins=["*"]')


def test_detecta_html_sin_sanitizar_solo_en_frontend():
    assert "html-sin-sanitizar" in _reglas("el.innerHTML = dato", path="ui.js")
    assert "html-sin-sanitizar" not in _reglas("el.innerHTML = dato", path="notas.md")


def test_codigo_limpio_no_genera_hallazgos():
    assert _reglas("def sumar(a, b):\n    return a + b") == set()


def test_la_severidad_viene_de_la_regla():
    hallazgos = scan([RepoFile(path="a.py", text='TOKEN = "abcdefghijklmnopqrst"')])
    assert hallazgos[0].severity is Severity.HIGH
