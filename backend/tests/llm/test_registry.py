import pytest

from app.llm.base import LLMProvider
from app.llm.registry import PROVIDERS, describe_providers, get_provider_class


def test_todos_los_proveedores_implementan_el_contrato():
    assert all(issubclass(c, LLMProvider) for c in PROVIDERS.values())


def test_cada_proveedor_tiene_clave_y_etiqueta():
    assert all(c.key and c.label for c in PROVIDERS.values())


def test_los_modelos_locales_no_exigen_clave():
    assert get_provider_class("ollama").requires_api_key is False


def test_un_proveedor_desconocido_falla_claro():
    with pytest.raises(ValueError):
        get_provider_class("inexistente")


def test_la_descripcion_es_serializable():
    assert {"key", "label", "requires_api_key", "supports_custom_base_url"} == set(
        describe_providers()[0]
    )
