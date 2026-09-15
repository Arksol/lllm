import pytest

from app.repos.exceptions import RepoError, UnsupportedHost
from app.repos.validators import parse_repo_url


def test_acepta_url_de_github():
    ref = parse_repo_url("https://github.com/psf/requests")
    assert (ref.host, ref.owner, ref.name) == ("github.com", "psf", "requests")


def test_acepta_url_sin_esquema():
    assert parse_repo_url("github.com/psf/requests").slug == "psf/requests"


def test_lee_la_rama_de_una_url_de_arbol():
    assert parse_repo_url("https://github.com/psf/requests/tree/main").ref == "main"


def test_acepta_hugging_face_con_prefijo_de_tipo():
    ref = parse_repo_url("https://huggingface.co/datasets/org/corpus")
    assert ref.slug == "org/corpus"


def test_rechaza_dominios_fuera_de_la_lista():
    with pytest.raises(UnsupportedHost):
        parse_repo_url("https://interno.local/a/b")


def test_rechaza_direcciones_internas():
    # ni por http (esquema no permitido) ni forzando https (dominio no permitido)
    with pytest.raises(RepoError):
        parse_repo_url("http://169.254.169.254/latest/meta-data")
    with pytest.raises(UnsupportedHost):
        parse_repo_url("https://169.254.169.254/a/b")


def test_rechaza_url_incompleta():
    with pytest.raises(RepoError):
        parse_repo_url("https://github.com/psf")
