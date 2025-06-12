📞 Proyecto de Contactabilidad con FastAPI
Este proyecto fue creado como una prueba de concepto para construir una API que permita gestionar procesos de contactabilidad, autenticación segura, y procesamiento de documentos como PDF, DOCX y Excel. Está desarrollado en Python utilizando FastAPI, ideal para construir servicios web modernos y de alto rendimiento.

🚀 Tecnologías Utilizadas
FastAPI – Framework para APIs rápidas y modernas

Uvicorn – Servidor ASGI ligero y veloz

Python-Jose – Para generación y verificación de tokens JWT

Passlib + Bcrypt – Para hashing y verificación segura de contraseñas

HTTPX – Cliente HTTP asíncrono

python-multipart – Para manejo de formularios y archivos

pandas – Procesamiento de datos tabulares

requests – Cliente HTTP sencillo y poderoso

python-docx – Lectura de archivos .docx

PyMuPDF – Lectura de archivos PDF

🛠️ Instalación Paso a Paso
Crea y activa un entorno virtual:

bash
Copiar
Editar
python3 -m venv .venv
source .venv/bin/activate
Instala las dependencias necesarias:

bash
Copiar
Editar
pip install fastapi uvicorn python-jose passlib bcrypt==3.2.2 httpx python-multipart pandas requests python-docx PyMuPDF
Ejecuta la aplicación:

bash
Copiar
Editar
uvicorn main:app --reload
Visita tu API en:

cpp
Copiar
Editar
http://127.0.0.1:8000
Y la documentación interactiva en:

arduino
Copiar
Editar
http://127.0.0.1:8000/docs
🔐 Credenciales de Prueba
Puedes autenticarte usando:

Usuario: admin

Contraseña: secret123

📁 Estructura del Proyecto
bash
Copiar
Editar
.
├── main.py               # Punto de entrada principal de la aplicación
├── auth.py               # Manejo de autenticación y generación de tokens
├── dependencies.py       # Funciones comunes para dependencias como el usuario actual
├── requirements.txt      # Lista de dependencias del proyecto
├── .venv/                # Entorno virtual (no subir a GitHub)
🌱 Próximas Mejoras
Gestión de usuarios desde una base de datos real

Soporte para múltiples roles y permisos

Procesamiento avanzado de documentos (OCR, NLP)

Despliegue en la nube con Docker

📄 Licencia
Este proyecto es de libre uso con fines educativos o de pruebas. ¡Adáptalo a tus necesidades!
