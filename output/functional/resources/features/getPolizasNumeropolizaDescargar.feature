@regression @api

Feature: Obtiene los datos del documento de la poliza por su número de póliza.

Background:
  Given url baseUrl
  * def configHeader = karate.call('classpath:karate-config.js').buildHeaders({})

@smoke @happy-path @regression
Scenario Outline: Obtener descarga de polizas exitosamente
  # Caso exitoso: obtener con parámetros válidos
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'

  Examples:
    | expectedStatus |
    | 200            |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar Transaccion-Id requerido
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName     |
    | Transaccion-Id |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de Transaccion-Id
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName     | invalidValue |
    | Transaccion-Id | 12345        |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar Aplicacion-Id requerido
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName    |
    | Aplicacion-Id |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de Aplicacion-Id
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName    | invalidValue |
    | Aplicacion-Id | 12345        |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar Nombre-Aplicacion requerido
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName        |
    | Nombre-Aplicacion |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de Nombre-Aplicacion
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName        | invalidValue |
    | Nombre-Aplicacion | 12345        |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar Usuario-Consumidor-Id requerido
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName            |
    | Usuario-Consumidor-Id |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de Usuario-Consumidor-Id
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName            | invalidValue |
    | Usuario-Consumidor-Id | 12345        |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar Nombre-Servicio-Consumidor requerido
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName                 |
    | Nombre-Servicio-Consumidor |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de Nombre-Servicio-Consumidor
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName                 | invalidValue |
    | Nombre-Servicio-Consumidor | 12345        |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar Ocp-Apim-Subscription-Key requerido
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName                |
    | Ocp-Apim-Subscription-Key |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de Ocp-Apim-Subscription-Key
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName                | invalidValue |
    | Ocp-Apim-Subscription-Key | 12345        |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud con datos inválidos
  # Tests que deben retornar Bad Request (400)
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.error == '#string'

  Examples:
    | expectedStatus | numeroPoliza |
    | 400            |              |
    | 400            |              |
    | 400            | 12345        |
    | 400            |              |

@error @authentication @get @regression
Scenario Outline: Rechazar solicitud sin autenticación
  # Tests que deben retornar Access Denied (401)
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.code == '#string'

  Examples:
    | expectedStatus |
    | 401            |

@error @server-error @get @regression
Scenario Outline: Manejar error interno del servidor
  # Tests que deben retornar Internal Server Error (500)
  * def numeroPoliza = '<numeroPoliza>'
  Given path '/polizas/', numeroPoliza, '/descargar'
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'

  Examples:
    | expectedStatus |
    | 500            |