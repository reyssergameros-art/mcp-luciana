@regression @api

Feature: Obtener prioridad por ID

Background:
  Given url baseUrl
  * def configHeader = karate.call('classpath:karate-config.js').buildHeaders({})

@smoke @happy-path @regression
Scenario Outline: Obtener priorities exitosamente
  # Caso exitoso: obtener con parámetros válidos
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'

  Examples:
    | id          | expectedStatus |
    |             | 200            |
    | 1           | 200            |
    | valid_value | 200            |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-correlation-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName       |
    | x-correlation-id |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-correlation-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName       | invalidValue |
    | x-correlation-id | invalid-uuid |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-request-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName   |
    | x-request-id |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-request-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName   | invalidValue |
    | x-request-id | invalid-uuid |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-transaction-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName       |
    | x-transaction-id |

@error @validation @invalid-type @get @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-transaction-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method GET
  Then status 400

  Examples:
    | headerName       | invalidValue |
    | x-transaction-id | invalid-uuid |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud con datos inválidos
  # Tests que deben retornar Bad Request (400)
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.error == '#string'

  Examples:
    | id          | expectedStatus |
    |             | 400            |
    |             | 400            |
    | 12345       | 400            |
    | 1           | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |
    | valid_value | 400            |

@error @not-found @get @status404 @regression
Scenario Outline: Rechazar solicitud de recurso inexistente
  # Tests que deben retornar Not Found (404)
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.message == '#string'

  Examples:
    | id     | expectedStatus |
    | 999999 | 404            |