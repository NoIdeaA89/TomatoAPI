def test_registro_exitoso(client):
    r = client.post(
        "/auth/register",
        json={"nombre": "Ana Rojas", "email": "  ANA@Example.com ", "password": "secreto1"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["access_token"]
    assert body["user"]["nombre"] == "Ana Rojas"
    assert body["user"]["email"] == "ana@example.com"
    assert "password" not in str(body)


def test_registro_con_correo_repetido(client):
    datos = {"nombre": "Ana", "email": "ana@example.com", "password": "secreto1"}
    assert client.post("/auth/register", json=datos).status_code == 201
    r = client.post("/auth/register", json=datos)
    assert r.status_code == 409
    assert r.json()["detail"] == "Ya existe una cuenta con ese correo."


def test_registro_con_datos_invalidos(client):
    r = client.post("/auth/register", json={"nombre": "Ana", "email": "no-es-correo", "password": "secreto1"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["msg"] == "Correo no válido."

    r = client.post("/auth/register", json={"nombre": "Ana", "email": "a@b.cl", "password": "123"})
    assert r.status_code == 422


def test_login(client):
    client.post("/auth/register", json={"nombre": "Ana", "email": "ana@example.com", "password": "secreto1"})
    ok = client.post("/auth/login", json={"email": "ANA@example.com", "password": "secreto1"})
    assert ok.status_code == 200
    assert ok.json()["access_token"]
    assert ok.json()["user"]["email"] == "ana@example.com"


def test_login_con_credenciales_incorrectas(client):
    client.post("/auth/register", json={"nombre": "Ana", "email": "ana@example.com", "password": "secreto1"})
    mala = client.post("/auth/login", json={"email": "ana@example.com", "password": "otra-clave"})
    assert mala.status_code == 401
    assert mala.json()["detail"] == "Correo o contraseña incorrectos."
    inexistente = client.post("/auth/login", json={"email": "nadie@example.com", "password": "secreto1"})
    assert inexistente.status_code == 401


def test_me(client, auth):
    r = client.get("/auth/me", headers=auth)
    assert r.status_code == 200
    assert r.json()["email"] == "ana@example.com"


def test_me_sin_token_o_con_token_invalido(client):
    assert client.get("/auth/me").status_code == 401
    r = client.get("/auth/me", headers={"Authorization": "Bearer basura"})
    assert r.status_code == 401
