@regression @api

Feature: Eliminar prioridad

Background:
  Given url baseUrl
  * def configHeader = karate.call('classpath:karate-config.js').buildHeaders({})

@smoke @happy-path @regression
Scenario Outline: Eliminar priorities exitosamente
  # Caso exitoso: eliminar con parámetros válidos
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  When method DELETE
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'

  Examples:
    | id          | expectedStatus |
    |             | 204            |
    | 1           | 204            |
    | valid_value | 204            |

@error @validation @delete @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-correlation-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method DELETE
  Then status 400

  Examples:
    | headerName       |
    | x-correlation-id |

@error @validation @invalid-type @delete @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-correlation-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method DELETE
  Then status 400

  Examples:
    | headerName       | invalidValue |
    | x-correlation-id | invalid-uuid |

@error @validation @delete @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-request-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method DELETE
  Then status 400

  Examples:
    | headerName   |
    | x-request-id |

@error @validation @invalid-type @delete @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-request-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method DELETE
  Then status 400

  Examples:
    | headerName   | invalidValue |
    | x-request-id | invalid-uuid |

@error @validation @delete @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-transaction-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  When method DELETE
  Then status 400

  Examples:
    | headerName       |
    | x-transaction-id |

@error @validation @invalid-type @delete @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-transaction-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  When method DELETE
  Then status 400

  Examples:
    | headerName       | invalidValue |
    | x-transaction-id | invalid-uuid |

@error @validation @delete @regression
Scenario Outline: Rechazar solicitud con datos inválidos
  # Tests que deben retornar Bad Request (400)
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  When method DELETE
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

@error @not-found @delete @status404 @regression
Scenario Outline: Rechazar solicitud de recurso inexistente
  # Tests que deben retornar Not Found (404)
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  When method DELETE
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.message == '#string'

  Examples:
    | id     | expectedStatus |
    | 999999 | 404            |