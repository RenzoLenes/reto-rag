#!/bin/bash

# Script para construir y ejecutar RAG Chatbot con Docker
# Uso: ./docker-run.sh [build|run|stop|logs|clean]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  RAG Chatbot Docker Script${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Función para verificar si Docker está ejecutándose
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker no está ejecutándose. Por favor inicia Docker Desktop."
        exit 1
    fi
}

# Función para verificar si existe el archivo .env
check_env_file() {
    if [ ! -f .env ]; then
        print_warning "Archivo .env no encontrado. Creando archivo de ejemplo..."
        cat > .env << EOF
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
EOF
        print_warning "Por favor edita el archivo .env con tus credenciales reales antes de continuar."
        exit 1
    fi
}

# Función para construir la imagen
build_image() {
    print_message "Construyendo imagen Docker..."
    docker build -t rag-chatbot-backend .
    print_message "Imagen construida exitosamente!"
}

# Función para ejecutar con Docker Compose
run_compose() {
    print_message "Iniciando servicios con Docker Compose..."
    docker-compose up -d
    print_message "Servicios iniciados!"
    print_message "Backend disponible en: http://localhost:8000"
    print_message "API Docs: http://localhost:8000/docs"
    print_message "Health Check: http://localhost:8000/health"
}

# Función para ejecutar solo el backend
run_backend() {
    print_message "Iniciando solo el backend..."
    docker run -d \
        --name rag-chatbot-backend \
        -p 8000:8000 \
        --env-file .env \
        --rm \
        rag-chatbot-backend
    print_message "Backend iniciado en http://localhost:8000"
}

# Función para detener servicios
stop_services() {
    print_message "Deteniendo servicios..."
    docker-compose down
    print_message "Servicios detenidos!"
}

# Función para mostrar logs
show_logs() {
    print_message "Mostrando logs..."
    docker-compose logs -f
}

# Función para limpiar
clean_up() {
    print_message "Limpiando contenedores e imágenes..."
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    print_message "Limpieza completada!"
}

# Función para mostrar estado
show_status() {
    print_message "Estado de los servicios:"
    docker-compose ps
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  build   - Construir imagen Docker"
    echo "  run     - Ejecutar con Docker Compose"
    echo "  backend - Ejecutar solo el backend"
    echo "  stop    - Detener servicios"
    echo "  logs    - Mostrar logs"
    echo "  status  - Mostrar estado de servicios"
    echo "  clean   - Limpiar contenedores e imágenes"
    echo "  help    - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 build    # Construir imagen"
    echo "  $0 run      # Ejecutar servicios"
    echo "  $0 logs     # Ver logs"
}

# Función principal
main() {
    print_header
    
    case "${1:-help}" in
        build)
            check_docker
            build_image
            ;;
        run)
            check_docker
            check_env_file
            build_image
            run_compose
            ;;
        backend)
            check_docker
            check_env_file
            build_image
            run_backend
            ;;
        stop)
            check_docker
            stop_services
            ;;
        logs)
            check_docker
            show_logs
            ;;
        status)
            check_docker
            show_status
            ;;
        clean)
            check_docker
            clean_up
            ;;
        help|*)
            show_help
            ;;
    esac
}

# Ejecutar función principal
main "$@"
