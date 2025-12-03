@regression @get

Feature: Obtiene los datos del documento de la poliza por su número de póliza.

Background:
  * def numeroPoliza = karate.get('numeroPoliza', '1')
  Given url baseUrl
  And path '/polizas/{numeroPoliza}/descargar'
  * def configHeader = headersDefaultEndpoint

@get @smoke @happyPath
Scenario Outline: Verificar éxito en GET con datos válidos
  # Tests con datos válidos que deben ser exitosos
  * def numeroPoliza = '<numeroPoliza>'
  * headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match responseType == 'json'

  Examples:
    | testName                                                       | expectedStatus | priority |
    | GET /polizas/{numeroPoliza}/descargar - OK - Request succeeded | 200            | high     |

@status400 @get @negativeTest @regression
Scenario Outline: Verificar que el servicio responda Bad Request con datos inválidos
  # Tests que deben retornar Bad Request (400)
  * def numeroPoliza = '<numeroPoliza>'
  * headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | testName                                                                              | expectedStatus | priority | Aplicacion-Id | Nombre-Aplicacion | Nombre-Servicio-Consumidor | Ocp-Apim-Subscription-Key | Transaccion-Id | Usuario-Consumidor-Id | numeroPoliza |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Transaccion-Id (required)             | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Transaccion-Id (required)             | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Transaccion-Id (type)                 | 400            | low      |               |                   |                            |                           | 12345          |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Aplicacion-Id (required)              | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Aplicacion-Id (required)              | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Aplicacion-Id (type)                  | 400            | low      | 12345         |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Nombre-Aplicacion (required)          | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Nombre-Aplicacion (required)          | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Nombre-Aplicacion (type)              | 400            | low      |               | 12345             |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Usuario-Consumidor-Id (required)      | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Usuario-Consumidor-Id (required)      | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Usuario-Consumidor-Id (type)          | 400            | low      |               |                   |                            |                           |                | 12345                 |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Nombre-Servicio-Consumidor (required) | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Nombre-Servicio-Consumidor (required) | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Nombre-Servicio-Consumidor (type)     | 400            | low      |               |                   | 12345                      |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Ocp-Apim-Subscription-Key (required)  | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Ocp-Apim-Subscription-Key (required)  | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid Ocp-Apim-Subscription-Key (type)      | 400            | low      |               |                   |                            | 12345                     |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid numeroPoliza (required)               | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid numeroPoliza (required)               | 400            | high     |               |                   |                            |                           |                |                       |              |
    | GET /polizas/{numeroPoliza}/descargar - Invalid numeroPoliza (type)                   | 400            | low      |               |                   |                            |                           |                |                       | 12345        |
    | GET /polizas/{numeroPoliza}/descargar - Bad Request - Invalid request data            | 400            | high     |               |                   |                            |                           |                |                       |              |

@get @status401 @negativeTest @regression
Scenario Outline: Verificar que el servicio responda Access Denied sin autenticación
  # Tests que deben retornar Access Denied (401)
  * def numeroPoliza = '<numeroPoliza>'
  * headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | testName                                                                       | expectedStatus | priority |
    | GET /polizas/{numeroPoliza}/descargar - Unauthorized - Authentication required | 401            | high     |

@status500 @get @negativeTest @regression
Scenario Outline: Verificar que el servicio responda Internal Server Error en error interno
  # Tests que deben retornar Internal Server Error (500)
  * def numeroPoliza = '<numeroPoliza>'
  * headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | testName                                                      | expectedStatus | priority |
    | GET /polizas/{numeroPoliza}/descargar - Internal Server Error | 500            | medium   |