#!/usr/bin/env python3
"""
📦 INSTALADOR AUTOMÁTICO DEL ARCHIVO DE VECTOR
==============================================
Este script configura todo el proyecto desde cero:
- Verifica e instala dependencias
- Configura MySQL
- Crea la base de datos
- Migra los modelos
- Carga las técnicas de los HTMLs
- Ejecuta el servidor
"""

import os
import sys
import subprocess
import time
import platform
import getpass

# Colores para la terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")

def print_step(text):
    print(f"\n{Colors.CYAN}➜ {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️ {text}{Colors.END}")

def run_command(cmd, description=None):
    """Ejecuta un comando y muestra su salida"""
    if description:
        print_step(description)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout:
                print(result.stdout.strip())
            return True
        else:
            if result.stderr:
                print_error(result.stderr.strip())
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def check_mysql():
    """Verifica si MySQL está instalado"""
    print_step("Verificando MySQL...")
    try:
        result = subprocess.run("mysql --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"MySQL encontrado: {result.stdout.strip().split()[4]}")
            return True
        else:
            print_warning("MySQL no encontrado")
            return False
    except:
        return False

def install_mysql():
    """Instala MySQL en sistemas Linux"""
    print_step("Instalando MySQL...")
    if platform.system() == "Linux":
        if os.path.exists("/usr/bin/apt"):
            commands = [
                "sudo apt update",
                "sudo apt install -y mysql-server mysql-client libmysqlclient-dev"
            ]
            for cmd in commands:
                if not run_command(cmd):
                    print_error("Error instalando MySQL")
                    return False
            return True
        elif os.path.exists("/usr/bin/yum"):
            commands = [
                "sudo yum install -y mysql-server mysql-client mysql-devel"
            ]
            for cmd in commands:
                if not run_command(cmd):
                    print_error("Error instalando MySQL")
                    return False
            return True
    print_warning("Sistema no soportado para instalación automática de MySQL")
    return False

def setup_mysql():
    """Configura MySQL y crea la base de datos"""
    print_step("Configurando MySQL...")
    
    # Verificar si MySQL está corriendo
    run_command("sudo service mysql start", "Iniciando MySQL")
    time.sleep(2)
    
    # Crear base de datos y usuario
    print_step("Creando base de datos y usuario...")
    
    # Intentar con diferentes contraseñas
    passwords = ['root123', 'root', '', '123456']
    success = False
    
    for pwd in passwords:
        print(f"  Probando con contraseña: {'***' if pwd else 'vacía'}")
        
        # Crear base de datos
        cmd = f"mysql -u root -p{pwd} -e 'CREATE DATABASE IF NOT EXISTS lms_vector_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;' 2>/dev/null"
        if subprocess.run(cmd, shell=True).returncode == 0:
            # Crear usuario
            cmd2 = f"mysql -u root -p{pwd} -e \"CREATE USER IF NOT EXISTS 'vector_user'@'localhost' IDENTIFIED BY 'vector_pass_123';\" 2>/dev/null"
            subprocess.run(cmd2, shell=True)
            
            # Dar permisos
            cmd3 = f"mysql -u root -p{pwd} -e \"GRANT ALL PRIVILEGES ON lms_vector_db.* TO 'vector_user'@'localhost';\" 2>/dev/null"
            subprocess.run(cmd3, shell=True)
            
            cmd4 = f"mysql -u root -p{pwd} -e 'FLUSH PRIVILEGES;' 2>/dev/null"
            subprocess.run(cmd4, shell=True)
            
            print_success(f"Base de datos creada con contraseña root: {pwd}")
            success = True
            break
    
    if not success:
        print_warning("No se pudo configurar MySQL automáticamente")
        print("  Intenta manualmente: sudo mysql")
        print("  CREATE DATABASE lms_vector_db;")
        print("  CREATE USER 'vector_user'@'localhost' IDENTIFIED BY 'vector_pass_123';")
        print("  GRANT ALL PRIVILEGES ON lms_vector_db.* TO 'vector_user'@'localhost';")
        return False
    
    return True

def check_python_deps():
    """Verifica e instala dependencias de Python"""
    print_step("Instalando dependencias de Python...")
    
    if not os.path.exists("requirements.txt"):
        print_warning("requirements.txt no encontrado, creando...")
        with open("requirements.txt", "w") as f:
            f.write("""Django==4.2.7
mysqlclient==2.2.0
django-cors-headers==4.3.1
djangorestframework==3.14.0
Pillow==10.1.0
""")
    
    # Verificar pip
    if not run_command("pip --version", "Verificando pip"):
        print_error("pip no está instalado")
        return False
    
    # Instalar dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        print_error("Error instalando dependencias")
        return False
    
    return True

def setup_django():
    """Configura Django y migra la base de datos"""
    print_step("Configurando Django...")
    
    # Hacer migraciones
    if not run_command("python manage.py makemigrations", "Creando migraciones"):
        print_error("Error creando migraciones")
        return False
    
    if not run_command("python manage.py migrate", "Migrando base de datos"):
        print_error("Error migrando base de datos")
        return False
    
    return True

def load_data():
    """Carga los datos de los HTMLs"""
    print_step("Cargando técnicas de los HTMLs...")
    
    if os.path.exists("extraer_tecnicas.py"):
        if not run_command("python extraer_tecnicas.py", "Extrayendo técnicas"):
            print_warning("Error extrayendo técnicas, continuando...")
    else:
        print_warning("extraer_tecnicas.py no encontrado")
    
    # También ejecutar el generador de lecciones si existe
    if os.path.exists("generate_lessons.py"):
        if not run_command("python generate_lessons.py", "Generando lecciones adicionales"):
            print_warning("Error generando lecciones, continuando...")
    
    return True

def create_superuser():
    """Crea un superusuario para Django"""
    print_step("Creando superusuario...")
    
    # Verificar si ya existe un superusuario
    check_cmd = "python manage.py shell -c 'from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())'"
    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
    
    if "True" in result.stdout:
        print_success("Ya existe un superusuario")
        return True
    
    print_warning("No hay superusuario. Creando uno...")
    print("  Usuario: admin")
    print("  Email: admin@vector.com")
    print("  Contraseña: admin123")
    
    create_cmd = """python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@vector.com', 'admin123')
    print('Superusuario creado: admin/admin123')
" """
    subprocess.run(create_cmd, shell=True)
    
    return True

def show_summary():
    """Muestra el resumen final"""
    print_header("📊 RESUMEN FINAL")
    
    # Contar lecciones
    cmd = "python manage.py shell -c 'from core.models import Lesson; print(Lesson.objects.count())'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    lessons = result.stdout.strip() if result.stdout else "0"
    
    # Contar cursos
    cmd = "python manage.py shell -c 'from core.models import Course; print(Course.objects.filter(is_active=True).count())'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    courses = result.stdout.strip() if result.stdout else "0"
    
    print(f"\n  {Colors.GREEN}📖 Total lecciones: {Colors.YELLOW}{lessons}{Colors.END}")
    print(f"  {Colors.GREEN}📚 Total cursos: {Colors.YELLOW}{courses}{Colors.END}")
    print(f"\n  {Colors.CYAN}🌐 Accede a: {Colors.BOLD}http://localhost:8000{Colors.END}")
    print(f"  {Colors.CYAN}🔑 Admin: {Colors.BOLD}http://localhost:8000/admin{Colors.END}")
    print(f"  {Colors.CYAN}👤 Usuario: {Colors.BOLD}admin{Colors.END}")
    print(f"  {Colors.CYAN}🔑 Contraseña: {Colors.BOLD}admin123{Colors.END}")

def main():
    """Función principal del instalador"""
    print_header("📦 INSTALADOR DEL ARCHIVO DE VECTOR")
    print("\n  Este script configurará automáticamente el Archivo de Vector")
    print("  Incluye: Django, MySQL, base de datos, técnicas y servidor")
    print("\n  Presiona Ctrl+C en cualquier momento para cancelar")
    
    input("\n  Presiona Enter para continuar...")
    
    # 1. Verificar Python
    print_step(f"Python: {sys.version.split()[0]}")
    
    # 2. Verificar/Instalar MySQL
    if not check_mysql():
        if platform.system() == "Linux":
            print_warning("Instalando MySQL...")
            if not install_mysql():
                print_warning("No se pudo instalar MySQL automáticamente")
        else:
            print_warning("MySQL no encontrado. Instálalo manualmente.")
            print("  Windows: https://dev.mysql.com/downloads/installer/")
            print("  Mac: brew install mysql")
    
    # 3. Configurar MySQL
    setup_mysql()
    
    # 4. Instalar dependencias de Python
    if not check_python_deps():
        print_error("Error instalando dependencias")
        sys.exit(1)
    
    # 5. Configurar Django
    if not setup_django():
        print_error("Error configurando Django")
        sys.exit(1)
    
    # 6. Cargar datos
    load_data()
    
    # 7. Crear superusuario
    create_superuser()
    
    # 8. Mostrar resumen
    show_summary()
    
    # 9. Preguntar si quiere ejecutar el servidor
    print("\n")
    response = input(f"{Colors.YELLOW}¿Quieres ejecutar el servidor ahora? (s/n): {Colors.END}")
    if response.lower() in ['s', 'si', 'yes', 'y']:
        print_step("Ejecutando servidor...")
        print(f"{Colors.CYAN}  Servidor iniciado en: http://localhost:8000{Colors.END}")
        print(f"{Colors.CYAN}  Presiona Ctrl+C para detener{Colors.END}")
        subprocess.run("python manage.py runserver", shell=True)
    else:
        print_step("¡Instalación completada!")
        print("  Para iniciar el servidor manualmente:")
        print("  python manage.py runserver")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + Colors.YELLOW + "👋 Instalación cancelada por el usuario" + Colors.END)
        sys.exit(0)
