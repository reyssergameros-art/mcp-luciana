# MCP Luciana - API Testing Automation Tool

Servidor MCP para generación automática de casos de prueba y features de Karate usando técnicas ISTQB v4.

## 🎯 Características

- **Análisis de Swagger**: Analiza especificaciones OpenAPI/Swagger desde URLs o archivos locales
- **Generación de Casos de Prueba**: Genera casos de prueba usando técnicas ISTQB v4:
  - Partición de Equivalencia (EP)
  - Análisis de Valores Límite (BVA) - 2-value y 3-value
- **Generación de Features Karate**: Convierte casos de prueba a features BDD ejecutables de Karate
- **Configuración Dinámica**: Sin datos hardcodeados, completamente extensible mediante configuración

## 📋 Prerrequisitos

- **Windows 10/11** (o otro SO con ajustes apropiados)
- **Python 3.13 o superior** - [Descargar aquí](https://www.python.org/downloads/)
- **Git** - [Descargar aquí](https://git-scm.com/downloads)

## 🚀 Instalación - Paso a Paso

### **Paso 1: Verificar Python**

```powershell
python --version
```

Debe mostrar: `Python 3.13.x` o superior

Si no tienes Python 3.13+, descárgalo desde [python.org](https://www.python.org/downloads/)

---

### **Paso 2: Instalar uv (Gestor de Paquetes Python)**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Actualizar PATH (cierra y abre PowerShell, o ejecuta):**
```powershell
$env:PATH = "$env:LOCALAPPDATA\Programs\uv;$env:PATH"
```

**Verificar instalación:**
```powershell
uv --version
```

---

### **Paso 3: Clonar el Repositorio**

```powershell
# Navegar al directorio donde quieres el proyecto
cd C:\Users\<TuUsuario>\Desktop\mcp

# Clonar el repositorio
git clone https://github.com/reyssergameros-art/mcp-luciana.git

# Entrar al directorio del proyecto
cd mcp-luciana
```

> Reemplaza `<TuUsuario>` con tu nombre de usuario de Windows

---

### **Paso 4: Crear el Entorno Virtual**

```powershell
uv venv
```

Esto crea un directorio `.venv` en tu proyecto con Python aislado.

---

### **Paso 5: Activar el Entorno Virtual**

```powershell
.venv\Scripts\Activate.ps1
```

**Resultado esperado:** Verás `(.venv)` o el nombre del proyecto al inicio de tu prompt.

> **⚠️ Si obtienes error de política de ejecución:**
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Luego intenta activar nuevamente: `.venv\Scripts\Activate.ps1`

---

### **Paso 6: Instalar Dependencias del Proyecto**

```powershell
uv pip install -e .
```

Esto instala todas las dependencias desde `pyproject.toml`:
- `fastmcp>=0.1.0` - Framework del servidor MCP
- `pydantic>=2.0.0` - Validación de datos
- `pydantic-settings>=2.0.0` - Gestión de configuración
- `httpx>=0.24.0` - Cliente HTTP para APIs
- `pyyaml>=6.0` - Parser de YAML

**Verificar instalación exitosa:**
```powershell
python -c "import fastmcp; print('✓ fastmcp instalado correctamente')"
```

---

### **Paso 7: Configurar Intérprete de Python en VS Code (Opcional)**

Si usas Visual Studio Code:

1. Presiona `Ctrl+Shift+P`
2. Escribe y selecciona: `Python: Select Interpreter`
3. Selecciona: `.venv\Scripts\python.exe` (debe aparecer con la ruta completa del proyecto)

---

## 📝 Resumen - Todos los Comandos en Orden

```powershell
# 1. Verificar Python 3.13+
python --version

# 2. Instalar uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Verificar uv
uv --version

# 4. Clonar repositorio
cd C:\Users\<TuUsuario>\Desktop\mcp
git clone https://github.com/reyssergameros-art/mcp-luciana.git
cd mcp-luciana

# 5. Crear entorno virtual
uv venv

# 6. Activar entorno virtual
.venv\Scripts\Activate.ps1

# 7. Instalar dependencias
uv pip install -e .

# 8. Verificar instalación
python -c "import fastmcp; print('✓ Instalación completada exitosamente')"
```

---

## 🎮 Uso del MCP Server

### Iniciar el Servidor MCP

```powershell
# Asegúrate de tener el entorno virtual activado (.venv)
python main.py
```

El servidor se iniciará y escuchará solicitudes de herramientas MCP.

---

### Herramientas MCP Disponibles

#### 1. **swagger_analysis**
Analiza especificaciones Swagger/OpenAPI desde URL o archivos locales.

**Tipos de entrada soportados:**
- ✅ **URL HTTP/HTTPS**: `http://localhost:8080/v3/api-docs`
- ✅ **Archivo JSON local**: `C:\Users\user\mi-swagger.json` o `mi-swagger.json` (relativo)
- ✅ **Archivo YAML local**: `C:\Users\user\mi-swagger.yaml` o `mi-swagger.yaml` (relativo)
- ✅ **URI con prefijo**: `file://C:/Users/user/mi-swagger.json`

**Ejemplos de uso:**

**Desde URL:**
```json
{
  "swagger_url": "http://localhost:8080/v3/api-docs",
  "save_output": true
}
```

**Desde archivo JSON local (ruta absoluta):**
```json
{
  "swagger_url": "C:\\Users\\reyss\\Desktop\\mi-contrato.json",
  "save_output": true
}
```

**Desde archivo YAML local (ruta relativa):**
```json
{
  "swagger_url": "contratos/api-specification.yaml",
  "save_output": true
}
```

**Con prefijo file://:**
```json
{
  "swagger_url": "file://C:/Users/reyss/Desktop/swagger.json",
  "save_output": true
}
```

**Salida:** Análisis guardado en `output/swagger/<nombre-api>.json`

**Nota:** Los archivos locales deben tener extensión `.json`, `.yaml`, o `.yml`

---

#### 2. **generate_test_cases**
Genera casos de prueba usando técnicas ISTQB v4 (EP + BVA + Status Code Coverage).

**Técnicas aplicadas automáticamente:**
- ✅ **Equivalence Partitioning (EP)**: Particiones válidas e inválidas
- ✅ **Boundary Value Analysis (BVA)**: Valores límite (2-value y 3-value)
- ✅ **Status Code Coverage**: Al menos 1 test case por cada código HTTP (200, 201, 204, 400, 404, 409, etc.)

**Ejemplo de uso:**
```json
{
  "swagger_analysis_file": "output/swagger/gestiónDePrioridadesApi.json",
  "bva_version": "both",
  "save_output": true
}
```

**Opciones:**
- `bva_version`: `"2-value"`, `"3-value"`, o `"both"` (por defecto)
- `endpoint_filter`: Filtrar por endpoint específico (opcional)
- `method_filter`: Filtrar por método HTTP (opcional)

**Salida:** Casos de prueba guardados en `output/test_cases/<metodo>_<endpoint>.json`

**Novedad:** Ahora incluye casos de prueba específicos para:
- ✅ 200 OK - Solicitud exitosa
- ✅ 201 Created - Recurso creado
- ✅ 204 No Content - Sin contenido
- ✅ 400 Bad Request - Datos inválidos
- ✅ 404 Not Found - Recurso inexistente
- ✅ 409 Conflict - Conflicto de recursos
- ✅ Y cualquier otro código definido en el Swagger

---

#### 3. **generate_karate_features**
Genera archivos feature de Karate BDD desde casos de prueba.

**Mejora:** Ahora genera scenarios separados por código de estado HTTP con nombres descriptivos:
- ✅ Scenario para 200 OK (happy path)
- ✅ Scenario para 400 Bad Request con datos inválidos
- ✅ Scenario para 404 Not Found para recurso inexistente
- ✅ Scenario para 409 Conflict por duplicados
- ✅ Y más...

**Ejemplo de uso:**
```json
{
  "test_cases_directory": "output/test_cases",
  "base_url": "http://localhost:8080",
  "output_directory": "output/functional"
}
```

**Salida:**
- Features de Karate: `output/functional/resources/features/<recurso>/<metodo><endpoint>.feature`
- Configuración Karate: `output/functional/karate-config.js`

---

### Flujo de Trabajo Completo

```powershell
# 1. Activar entorno virtual
.venv\Scripts\Activate.ps1

# 2. Iniciar servidor MCP
python main.py

# En tu cliente MCP (ej: Claude Desktop, Cline):

# 3. Analizar Swagger
# Usar herramienta: swagger_analysis
# Input: {"swagger_url": "http://localhost:8080/v3/api-docs"}

# 4. Generar casos de prueba
# Usar herramienta: generate_test_cases
# Input: {"swagger_analysis_file": "output/swagger/gestiónDePrioridadesApi.json"}

# 5. Generar features de Karate
# Usar herramienta: generate_karate_features
# Input: {"test_cases_directory": "output/test_cases"}
```

---

## 📦 Portabilidad (Llevar a Otro Equipo)

Para transferir este proyecto a otra máquina:

### **En la Máquina Nueva:**

```powershell
# 1. Instalar Python 3.13+ (si no está instalado)
python --version

# 2. Instalar uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Clonar el repositorio
git clone https://github.com/reyssergameros-art/mcp-luciana.git
cd mcp-luciana

# 4. Crear entorno virtual
uv venv

# 5. Activar entorno virtual
.venv\Scripts\Activate.ps1

# 6. Instalar dependencias
uv pip install -e .

# 7. Listo para usar
python main.py
```

> **Importante:** El `.gitignore` excluye `.venv/`, `__pycache__/`, y `output/`, por lo que estos directorios se recrean automáticamente en la nueva máquina.

---

## 🏗️ Arquitectura del Proyecto

```
mcp-luciana/
├── main.py                     # Punto de entrada del servidor MCP
├── pyproject.toml              # Dependencias y configuración
├── src/
│   ├── presentation/
│   │   └── mcp_server.py       # Implementación del servidor MCP
│   ├── tools/
│   │   ├── swagger_analysis/   # Análisis de Swagger/OpenAPI
│   │   ├── test_generation/    # Generación de casos ISTQB
│   │   └── karate_generation/  # Generación de features Karate
│   └── shared/                 # Utilidades y configuración
└── output/                     # Archivos generados (se crea automáticamente)
    ├── swagger/                # Resultados de análisis Swagger
    ├── test_cases/             # Casos de prueba generados
    └── functional/             # Features de Karate
```

### Principios de Diseño

- **Clean Architecture:** Separación de capas (Domain, Application, Infrastructure)
- **SOLID Principles:** Código mantenible y extensible
- **Repository Pattern:** Abstracción del acceso a datos
- **Service Pattern:** Encapsulación de lógica de negocio
- **Value Objects:** Conceptos de dominio inmutables

---

## 🛠️ Solución de Problemas

### Error: "No se puede ejecutar scripts en este sistema"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "python no se reconoce como comando"
- Verifica que Python 3.13+ esté instalado
- Asegúrate de que Python esté en el PATH del sistema

### Error: "uv no se reconoce como comando"
- Cierra y abre PowerShell después de instalar uv
- O ejecuta: `$env:PATH = "$env:LOCALAPPDATA\Programs\uv;$env:PATH"`

### El entorno virtual no se activa
```powershell
# Alternativa usando Python directamente
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Verificar instalación de dependencias
```powershell
uv pip list
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 👤 Autor

**Reyssen Gameros**
- GitHub: [@reyssergameros-art](https://github.com/reyssergameros-art)

## 🤝 Contribuciones

¡Contribuciones, issues y solicitudes de features son bienvenidas!

## 📞 Soporte

Si encuentras algún problema:

1. Verifica que Python sea versión 3.13 o superior: `python --version`
2. Verifica que uv esté instalado: `uv --version`
3. Asegúrate de que el entorno virtual esté activado: Busca el prefijo `(.venv)`
4. Reinstala las dependencias: `uv pip install -e .`

Para más ayuda, abre un issue en el [repositorio de GitHub](https://github.com/reyssergameros-art/mcp-luciana/issues).
