class RepoError(Exception):
    """Fallo al resolver o descargar un repositorio."""


class UnsupportedHost(RepoError):
    """El dominio no esta en la lista permitida."""
