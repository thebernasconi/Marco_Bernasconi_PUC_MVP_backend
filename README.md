# MVP PUC Desenvolvimento FullStack - Marco Bernasconi

# AnotAí — Backend (Flask + SQLite + Flask-RESTX)

**Repositório do backend do projeto AnotAí (PUC — MVP Fullstack).**  
Este backend implementa uma API REST com Flask, SQLite e Flask-RESTX, oferecendo CRUD de **Usuários** e **Notas (Notes)**.  

---

## 🚀 Tecnologias
- Python 3.9+ (recomendado 3.10 ou superior)
- Flask
- Flask-RESTX (Swagger)
- Flask-SQLAlchemy
- Flask-CORS
- SQLite

---

## 📂 Estrutura
Marco_Bernasconi_PUC_MVP_backend/
- ├─app.py
- ├─extensions.py
- ├─models.py
- ├─resources/
- │ ├─ users.py
- │ └─ notes.py
- ├─requirements.txt
- └─README.md

---

## ⚙️ Instalação e execução (Windows)

1. Clone o repositório:
```powershell
git clone https://github.com/thebernasconi/Marco_Bernasconi_PUC_MVP_backend.git
cd <path do arquivo>
```
2. Crie e ative o ambiente virtual:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
3. Instale as dependências:
```powershell
pip install -r requirements.txt
```
4. Rode o servidor:
```powershell
python app.py
```
O backend ficará disponível em "http://127.0.0.1:5000".

---

## 📖 Documentação (Swagger)

Abra no navegador e busque por "http://127.0.0.1:5000/docs".

Os JSONS criados serão visívies em "http://127.0.0.1:5000/notes/" e "http://127.0.0.1:5000/users/".

## 📌 Endpoints principais

**Usuários**

- GET /users/ → lista todos
- POST /users/ → cria usuário
- GET /users/{id} → busca usuário
- PUT /users/{id} → atualiza usuário
- DELETE /users/{id} → apaga usuário (cascade apaga notas)

**Notas**

- GET /notes/ → lista todas
- POST /notes/ → cria nota
- GET /notes/{id} → busca nota
- PUT /notes/{id} → atualiza nota
- DELETE /notes/{id} → apaga nota

---

## 🗄️ Banco de dados

SQLite (arquivo .db).

**Para recriar o banco:**

```python
from app import db
db.drop_all()
db.create_all()
```
---
## 📝 Observações

CORS habilitado para permitir integração com frontend local (file://).






















