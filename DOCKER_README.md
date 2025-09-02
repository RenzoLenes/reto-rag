# 🐳 Docker Setup para RAG Chatbot

Este documento explica cómo configurar y ejecutar la aplicación RAG Chatbot usando Docker.

## 📋 Prerrequisitos

- Docker instalado en tu sistema
- Docker Compose instalado
- Variables de entorno configuradas

## 🚀 Configuración Rápida

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en el directorio raíz con las siguientes variables:

```bash
# Configuración de la aplicación
APP_ENV=production
APP_PORT=8000

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRES_SECONDS=86400

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_REGION=us-east-1
AWS_S3_BUCKET=your-s3-bucket-name

# AstraDB Configuration
ASTRA_DB_API_ENDPOINT=your-astra-db-endpoint
ASTRA_DB_APPLICATION_TOKEN=your-astra-db-token
ASTRA_DB_KEYSPACE=default_keyspace
ASTRA_DB_COLLECTION_USERS=users
ASTRA_DB_COLLECTION_SESSIONS=sessions
ASTRA_DB_COLLECTION_DOCUMENTS=documents
ASTRA_DB_COLLECTION_EMBEDDINGS=embeddings
ASTRA_DB_COLLECTION_MESSAGES=messages
```

### 2. Construir y Ejecutar

```bash
# Construir la imagen del backend
docker build -t rag-chatbot-backend .

# Ejecutar solo el backend
docker run -d \
  --name rag-chatbot-backend \
  -p 8000:8000 \
  --env-file .env \
  rag-chatbot-backend
```

### 3. Usar Docker Compose (Recomendado)

```bash
# Ejecutar backend y frontend juntos
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

## 🌐 Puertos y Comunicación

- **Backend**: Puerto 8000 (http://localhost:8000)
- **Frontend**: Puerto 3000 (http://localhost:3000)
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Configuración de CORS

El backend está configurado para permitir comunicación con el frontend en el puerto 3000. La configuración CORS se encuentra en `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar apropiadamente para producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📁 Estructura de Volúmenes

- `./documents:/app/documents`: Almacenamiento persistente de documentos
- Los documentos subidos se mantienen entre reinicios del contenedor

## 🐛 Troubleshooting

### Verificar que el contenedor esté ejecutándose
```bash
docker ps
```

### Ver logs del backend
```bash
docker logs rag-chatbot-backend
```

### Verificar conectividad
```bash
curl http://localhost:8000/health
```

### Reiniciar servicios
```bash
docker-compose restart
```

## 🚀 Comandos Útiles

```bash
# Reconstruir imagen después de cambios
docker-compose build --no-cache

# Ejecutar en modo desarrollo (con logs)
docker-compose up

# Ejecutar en background
docker-compose up -d

# Ver logs de un servicio específico
docker-compose logs -f backend

# Acceder al shell del contenedor
docker exec -it rag-chatbot-backend /bin/bash

# Limpiar contenedores e imágenes no utilizadas
docker system prune -a
```

## 🔒 Seguridad

- El contenedor se ejecuta como usuario no-root (`appuser`)
- Las variables sensibles se pasan a través de archivo `.env`
- El puerto 8000 está expuesto solo para desarrollo local

## 📝 Notas de Producción

Para producción, considera:
- Configurar CORS específicamente para tu dominio
- Usar un proxy reverso (nginx)
- Configurar SSL/TLS
- Implementar rate limiting
- Configurar logging centralizado
- Usar secrets de Docker para variables sensibles
