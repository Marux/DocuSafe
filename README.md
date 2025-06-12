API de Gestión de Archivos con Autenticación JWT
Este proyecto es una API REST construida con FastAPI que permite gestionar archivos con autenticación JWT. Incluye funcionalidades para subir, descargar, listar y eliminar archivos, así como unificar diferentes tipos de archivos en uno solo.

Características principales
Autenticación JWT mediante cookies o headers

CORS configurado para desarrollo

Endpoints protegidos con roles de usuario

Soporte para múltiples formatos de archivo (TXT, DOCX, XLSX, PDF)

Integración con webhooks (n8n)

Validación de seguridad contra path traversal

Requisitos
Python 3.7+

Las siguientes dependencias (ver requirements.txt):

fastapi==0.109.1
uvicorn==0.27.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==3.2.2
httpx==0.27.0
python-multipart==0.0.9

Instalación
Clona el repositorio

Crea un entorno virtual:

bash
python3 -m venv .venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows


pip install fastapi uvicorn python-jose passlib bcrypt==3.2.2 httpx python-multipart pandas requests python-docx PyMuPDF

Configuración
Antes de ejecutar la API, asegúrate de configurar:

SECRET_KEY en auth.py (usa una clave segura en producción)

ACCESS_TOKEN_EXPIRE_MINUTES para el tiempo de expiración del token

WEBHOOK_URL en main.py si deseas usar la integración con n8n

Uso
Iniciar el servidor
bash
uvicorn main:app --reload

La API estará disponible en http://localhost:8000 con documentación interactiva en /docs.

Endpoints principales
Autenticación
POST /token: Obtén un token JWT (credenciales por defecto: admin/secret123)

Operaciones con archivos
POST /upload: Sube un archivo (requiere autenticación)

GET /files: Lista todos los archivos disponibles

GET /files/{filename}: Descarga un archivo específico

DELETE /files/{filename}: Elimina un archivo

GET /unify-files: Une todos los archivos en un solo TXT y envía a webhook

Estructura del proyecto
text
.
├── main.py            # Punto de entrada de la API
├── auth.py            # Lógica de autenticación y JWT
├── storage/           # Directorio donde se guardan los archivos
├── README.md          # Este archivo
└── requirements.txt   # Dependencias del proyecto
Seguridad
Todos los endpoints (excepto /token) requieren autenticación

Las contraseñas se almacenan hasheadas con bcrypt

Los tokens JWT tienen tiempo de expiración

Validación contra path traversal en operaciones con archivos

Cookies HTTP-only para tokens

Ejemplo de uso
Obtener token:

bash
curl -X POST "http://localhost:8000/token" \
-H "Content-Type: application/json" \
-d '{"username":"admin","password":"secret123"}'
Subir archivo (con token en cookie):

bash
curl -X POST "http://localhost:8000/upload" \
-H "Cookie: access_token=Bearer <TU_TOKEN>" \
-F "file=@mi_archivo.txt"
Notas de producción
No usar la SECRET_KEY de ejemplo en producción

Configurar HTTPS en producción

Considerar usar una base de datos real en lugar del mock de usuarios

Ajustar políticas CORS para el entorno de producción

Licencia
Este proyecto está bajo la licencia MIT.
