def test_salud(client):
    assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_historial_vacio_al_inicio(client):
    assert isinstance(client.get("/api/v1/analysis/history").json(), list)


def test_rechaza_un_dominio_no_permitido(client):
    response = client.post(
        "/api/v1/analysis", json={"repo_url": "https://ejemplo.com/a/b", "mode": "junior"}
    )
    assert response.status_code == 400


def test_pide_configurar_modelo_antes_de_analizar(client):
    response = client.post(
        "/api/v1/analysis",
        json={"repo_url": "https://github.com/psf/requests", "mode": "junior"},
    )
    assert response.status_code == 409


def test_analisis_inexistente_devuelve_404(client):
    assert client.get("/api/v1/analysis/no-existe").status_code == 404


def test_el_catalogo_de_proveedores_no_esta_vacio(client):
    assert len(client.get("/api/v1/settings/providers").json()) >= 5
