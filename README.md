# 📁 API de Gestión de Archivos con Autenticación JWT

> Una API REST moderna construida con FastAPI para gestionar archivos de forma segura con autenticación JWT

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

## 🚀 Descripción

Este proyecto es una API REST construida con **FastAPI** que permite gestionar archivos con autenticación JWT. Incluye funcionalidades para subir, descargar, listar y eliminar archivos, así como unificar diferentes tipos de archivos en uno solo.

## ✨ Características principales

- 🔐 **Autenticación JWT** mediante cookies o headers
- 🌐 **CORS configurado** para desarrollo
- 🛡️ **Endpoints protegidos** con roles de usuario
- 📄 **Soporte múltiple** para formatos (TXT, DOCX, XLSX, PDF)
- 🔗 **Integración con webhooks** (n8n)
- 🛡️ **Validación de seguridad** contra path traversal

## 📋 Requisitos

- **Python 3.7+**
- Las siguientes dependencias principales:

```txt
fastapi==0.109.1
uvicorn==0.27.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==3.2.2
httpx==0.27.0
python-multipart==0.0.9
```

## 🛠️ Instalación

### 1. Clona el repositorio
```bash
git clone https://github.com/Marux/DocuSafe.git
cd DocuSafe
```

### 2. Crea un entorno virtual
```bash
# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instala las dependencias
```bash
pip install fastapi uvicorn python-jose passlib bcrypt==3.2.2 httpx python-multipart pandas requests python-docx PyMuPDF
```

## ⚙️ Configuración

Antes de ejecutar la API, asegúrate de configurar:

- 🔑 **SECRET_KEY** en `auth.py` (usa una clave segura en producción)
- ⏰ **ACCESS_TOKEN_EXPIRE_MINUTES** para el tiempo de expiración del token
- 🔗 **WEBHOOK_URL** en `main.py` si deseas usar la integración con n8n

## 🚀 Uso

### Iniciar el servidor
```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000` con documentación interactiva en `/docs`.

## 📚 Endpoints principales

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/token` | Obtén un token JWT |

**Credenciales por defecto:** `admin` / `secret123`

### 📁 Operaciones con archivos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/upload` | Sube un archivo | ✅ |
| `GET` | `/files` | Lista todos los archivos | ❌ |
| `GET` | `/files/{filename}` | Descarga un archivo específico | ❌ |
| `DELETE` | `/files/{filename}` | Elimina un archivo | ✅ |
| `GET` | `/unify-files` | Une archivos en TXT y envía a webhook | ✅ |

## 📂 Estructura del proyecto

```
.
├── 📄 main.py            # Punto de entrada de la API
├── 🔐 auth.py            # Lógica de autenticación y JWT
├── 📁 storage/           # Directorio donde se guardan los archivos
├── 📖 README.md          # Este archivo
└── 📋 requirements.txt   # Dependencias del proyecto
```

## 🛡️ Seguridad

- 🔒 Todos los endpoints (excepto `/token`) requieren autenticación
- 🔐 Las contraseñas se almacenan hasheadas con bcrypt
- ⏰ Los tokens JWT tienen tiempo de expiración
- 🛡️ Validación contra path traversal en operaciones con archivos
- 🍪 Cookies HTTP-only para tokens

## 💡 Ejemplo de uso

### Obtener token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret123"}'
```

### Subir archivo (con token en cookie)
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Cookie: access_token=Bearer <TU_TOKEN>" \
  -F "file=@mi_archivo.txt"
```

### Listar archivos
```bash
curl -X GET "http://localhost:8000/files"
```

### Descargar archivo
```bash
curl -X GET "http://localhost:8000/files/mi_archivo.txt" \
  --output mi_archivo.txt
```

## 🚀 Notas de producción

> ⚠️ **Importante para producción:**

- 🔑 No usar la `SECRET_KEY` de ejemplo en producción
- 🔒 Configurar HTTPS en producción
- 💾 Considerar usar una base de datos real en lugar del mock de usuarios
- 🌐 Ajustar políticas CORS para el entorno de producción
- 📝 Implementar logging adecuado
- 🔄 Configurar backups automáticos del directorio `storage/`

## 📄 Licencia

Este proyecto está bajo la **licencia MIT**.

---

<div align="center">

**¿Encontraste útil este proyecto? ¡Dale una ⭐ en GitHub!**

</div>
