# Librerías estándar
import datetime
import os
from typing import List, Optional
import pandas as pd
import requests

# Dependencias de terceros - Core
from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
    UploadFile,
)
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from jose import JWTError, jwt
from pydantic import BaseModel
import httpx

# Módulos locales
from auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)

app = FastAPI()

# Middleware para exponer cookies
@app.middleware("http")
async def expose_cookie_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in ["/openapi.json", "/docs", "/redoc"]:
        response.headers["Access-Control-Expose-Headers"] = "Set-Cookie"
    return response

# CORS Config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Autenticación centralizada ---
async def get_current_user(
    access_token: Optional[str] = Cookie(default=None, include_in_schema=False),
    authorization: Optional[str] = None
):
    if not access_token and not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no proporcionadas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        token = (
            access_token.replace("Bearer ", "") if access_token 
            else authorization.split(" ")[1] if authorization 
            else None
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (IndexError, JWTError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

# Modelos
class UserLogin(BaseModel):
    username: str
    password: str

# Mock DB
fake_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("secret123"),
    }
}

# --- Endpoints ---
@app.post("/token")
async def login(user_data: UserLogin, response: Response):
    user = fake_db.get(user_data.username)
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    
    token = create_access_token({"sub": user_data.username})
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        secure=False,
        samesite="lax",
        path="/"
    )
    return {"message": "Login exitoso"}

@app.post("/upload")
async def upload_file(
    file: UploadFile,
    current_user: dict = Depends(get_current_user)  # 👈 Dependencia de autenticación
):
    # Validar nombre único
    filepath = f"storage/{file.filename}"
    if os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un archivo con el nombre '{file.filename}'"
        )
    
    # Guardar archivo
    os.makedirs("storage", exist_ok=True)
    try:
        with open(filepath, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar: {str(e)}"
        )
    
    return {
        "status": "success",
        "file_info": {
            "original_name": file.filename,
            "saved_path": filepath,
            "size": os.path.getsize(filepath),
            "user": current_user.get("sub")
        }
    }
@app.get("/files", response_model=List[dict])
async def get_all_files(
    current_user: dict = Depends(get_current_user)  # 👈 Reutiliza tu autenticación
):
    """
    Lista todos los archivos subidos al servidor.
    Requiere autenticación JWT (cookie o header Authorization).
    """
    try:
        files = []
        storage_dir = "storage"
        
        if not os.path.exists(storage_dir):
            return JSONResponse(content=[], status_code=200)
        
        for filename in os.listdir(storage_dir):
            filepath = os.path.join(storage_dir, filename)
            if os.path.isfile(filepath):
                file_stat = os.stat(filepath)
                files.append({
                    "name": filename,
                    "path": filepath,
                    "size_bytes": file_stat.st_size,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "last_modified": datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "uploaded_by": current_user.get("sub", "unknown")  # 👈 Usa el usuario autenticado
                })
        
        return files
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer archivos: {str(e)}"
        )

@app.delete("/files/{filename}")
async def delete_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un archivo del servidor.
    Requiere autenticación JWT y que el archivo exista.
    """
    # Prevenir path traversal
    if "../" in filename or not filename.isprintable():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo inválido"
        )

    filepath = f"storage/{filename}"
    
    # Verificar si el archivo existe
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo '{filename}' no encontrado"
        )
    
    try:
        # Verificar que es un archivo (no directorio)
        if os.path.isfile(filepath):
            os.remove(filepath)
            return {
                "status": "success",
                "detail": f"Archivo '{filename}' eliminado correctamente",
                "metadata": {
                    "deleted_by": current_user.get("sub"),
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{filename}' no es un archivo válido"
            )
            
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este archivo"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar archivo: {str(e)}"
        )

@app.get("/files/{filename}", response_class=FileResponse)
async def download_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Descarga un archivo específico del servidor.
    
    Parámetros:
    - filename: Nombre del archivo a descargar (debe existir en el storage)
    
    Returns:
    - FileResponse: El archivo solicitado como respuesta de descarga
    - 404: Si el archivo no existe
    - 400: Si el nombre contiene caracteres inválidos
    - 403: Si no tienes permisos
    """
    # Prevenir path traversal y validar nombre
    if not filename or "../" in filename or not filename.isprintable():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo inválido"
        )

    filepath = f"storage/{filename}"
    
    # Verificar existencia del archivo
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo '{filename}' no encontrado"
        )
    
    # Verificar que es un archivo (no directorio)
    if not os.path.isfile(filepath):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{filename}' no es un archivo válido"
        )
    
    try:
        # Registrar la descarga (opcional)
        print(f"Usuario {current_user.get('sub')} descargó {filename}")
        
        # Devolver el archivo como respuesta de descarga
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/octet-stream'  # Tipo genérico para forzar descarga
        )
    
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este archivo"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar archivo: {str(e)}"
        )

WEBHOOK_URL = "http://localhost:5678/webhook/archivos_locales"  # Reemplaza con tu URL real de n8n

@app.get("/unify-files")
async def unify_files(
    current_user: dict = Depends(get_current_user)
):
    """
    Une todos los archivos en 'storage' en un único archivo TXT.
    Soporta: TXT, DOCX, XLSX/XLS, PDF
    """
    storage_dir = "storage"
    output_path = "storage/archivos_locales.txt"
    
    if not os.path.exists(storage_dir):
        raise HTTPException(status_code=404, detail="No hay archivos en storage")

    unified_content: List[str] = []

    for filename in os.listdir(storage_dir):
        filepath = os.path.join(storage_dir, filename)

        if not os.path.isfile(filepath) or filename == "archivos_locales.txt":
            continue

        try:
            ext = os.path.splitext(filename)[1].lower()
            file_header = f"\n--- {filename} ---\n"

            # TXT files
            if ext == ".txt":
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        unified_content.append(file_header + f.read())
                except UnicodeDecodeError:
                    # Fallback for other encodings
                    with open(filepath, "r", encoding="latin-1") as f:
                        unified_content.append(file_header + f.read())

            # Word documents
            elif ext == ".docx":
                try:
                    from docx import Document
                    doc = Document(filepath)
                    content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                    unified_content.append(file_header + content)
                except Exception as e:
                    unified_content.append(file_header + f"[Error leyendo DOCX: {str(e)}]")

            # Excel files
            elif ext in (".xlsx", ".xls"):
                try:
                    excel = pd.read_excel(filepath, sheet_name=None)
                    text = ""
                    for sheet_name, df in excel.items():
                        text += f"\n### Hoja: {sheet_name} ###\n{df.to_string(index=False)}\n"
                    unified_content.append(file_header + text)
                except Exception as e:
                    unified_content.append(file_header + f"[Error leyendo Excel: {str(e)}]")

            # PDF files
            elif ext == ".pdf":
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(filepath)
                    text = "\n".join([page.get_text() for page in doc])
                    unified_content.append(file_header + text)
                except Exception as e:
                    unified_content.append(file_header + f"[Error leyendo PDF: {str(e)}]")

            # Unsupported formats
            else:
                unified_content.append(file_header + f"[Formato no soportado: {ext}]")

        except Exception as e:
            unified_content.append(f"\n--- {filename} ---\n[Error inesperado: {str(e)}]")

    # Save unified file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(unified_content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo unificado: {str(e)}")

    # Enviar el contenido como texto plano en JSON a n8n
    try:
        with open(output_path, "r", encoding="utf-8") as file:
            text_content = file.read()
            data = {"text": text_content}
            response = requests.post(WEBHOOK_URL, json=data)
            response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar contenido a n8n: {str(e)}")

    return FileResponse(
        path=output_path,
        filename="archivos_locales.txt",
        media_type="text/plain"
    )