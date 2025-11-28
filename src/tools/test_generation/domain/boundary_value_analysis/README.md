# Boundary Value Analysis (BVA) - ISTQB v4

## Descripción

Implementación de la técnica de Análisis de Valores Límite según ISTQB v4, aplicada únicamente a **particiones ordenadas**.

## Definición ISTQB v4

> "El análisis de valores límite (BVA) es una técnica basada en el ejercicio de los límites de las particiones de equivalencia. Por lo tanto, **BVA solo se puede usar para particiones ordenadas**."

## Versiones de BVA

### BVA de 2 valores
- **Elementos de cobertura**: Boundary + 1 vecino
- **Ejemplo**: `maxLength=50` → Prueba `[50, 51]`
- Cobertura = (límites ejercidos / límites identificados) * 100%

### BVA de 3 valores  
- **Elementos de cobertura**: Boundary + 2 vecinos
- **Ejemplo**: `maxLength=50` → Prueba `[49, 50, 51]`
- **Más riguroso**: Detecta defectos que BVA de 2 valores podría omitir
- Ejemplo: Si `if (x ≤ 10)` se implementa como `if (x = 10)`, x=9 (BVA 3 valores) lo detecta

## Particiones Aplicables

### ✅ String (longitud ordenada)
- `minLength`: Límite mínimo de caracteres
- `maxLength`: Límite máximo de caracteres

### ✅ Numéricos (rango ordenado)
- `minimum`: Valor mínimo permitido
- `maximum`: Valor máximo permitido

### ✅ Arrays (cantidad ordenada)
- `minItems`: Mínimo número de elementos
- `maxItems`: Máximo número de elementos

### ❌ NO Aplicables
- Enums (no ordenados)
- Booleanos (no ordenados)
- Formatos sin límites numéricos

## Estructura del Código

```
test_generation/
├── domain/
│   └── boundary_value_analysis/
│       ├── models.py           # BVAResult, BVATestCase, BoundaryValue
│       └── exceptions.py       # BVAError, InvalidBoundaryError
├── application/
│   └── boundary_value_analysis/
│       └── services.py         # BVAService (orchestrator)
└── infrastructure/
    └── boundary_value_analysis/
        ├── boundary_identifier.py    # Identifica límites dinámicamente
        └── test_case_builder.py      # Genera casos de prueba
```

## Principios SOLID Aplicados

- **Single Responsibility**: Cada clase tiene una responsabilidad única
- **Open/Closed**: Extensible para nuevos tipos de límites
- **Dependency Inversion**: Servicios dependen de abstracciones
- **Separation of Concerns**: Domain, Application, Infrastructure separados

## Ejemplo de Uso

```python
# Via MCP Tool
result = await orchestrator.generate_boundary_value_tests(
    swagger_analysis_file="output/swagger/api.json",
    bva_version="3-value",
    save_output=True
)

# Resultado:
# - Límites identificados: 15
# - Casos de prueba generados: 45 (15 * 3 para BVA 3-value)
# - Cobertura: 100%
```

## Salida

Archivos JSON en `output/bva_tests/` con estructura:
```json
{
  "metadata": {
    "technique": "Boundary Value Analysis (3-value) - ISTQB v4",
    "endpoint": "/users",
    "http_method": "POST"
  },
  "metrics": {
    "boundaries_identified": 5,
    "coverage_percentage": 100.0,
    "coverage_items_tested": 15,
    "coverage_items_total": 15
  },
  "test_cases": [...]
}
```

## Diferencias con Partición de Equivalencia

| Aspecto | EP | BVA |
|---------|-----|-----|
| Aplicabilidad | Todas las particiones | Solo particiones ordenadas |
| Enfoque | Cualquier valor de la partición | Valores límite + vecinos |
| Cobertura | % de particiones | % de límites ejercidos |
| Complementariedad | Técnica base | Complementa EP |

## Referencias

- ISTQB Foundation Level Syllabus v4.0
- Craig 2002 (BVA 2-value)
- Koomen 2006, O'Regan 2019 (BVA 3-value)
