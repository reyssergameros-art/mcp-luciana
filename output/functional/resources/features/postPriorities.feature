@regression @api

Feature: Crear nueva prioridad

Background:
  Given url baseUrl
  * def configHeader = karate.call('classpath:karate-config.js').buildHeaders({})

@smoke @happy-path @regression
Scenario Outline: Crear priorities exitosamente
  # Caso exitoso: crear con parámetros válidos
  Given path '/priorities'
  And headers configHeader
  And request <requestBody>
  When method POST
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'

  Examples:
    | name                                                                   | expectedStatus | description                                                            | idPriority  |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                   | 201            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                   |             |
    |                                                                        | 201            |                                                                        |             |
    | aaa                                                                    | 201            | aaaaaaaa                                                               | 50          |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 201            | aaaaaaaa                                                               | 50          |
    | aaaaaaaa                                                               | 201            | aaa                                                                    | 50          |
    | aaaaaaaa                                                               | 201            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50          |
    | aaa                                                                    | 201            | aaaaaaaa                                                               | 50          |
    | aaaa                                                                   | 201            | aaaaaaaa                                                               | 50          |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  | 201            | aaaaaaaa                                                               | 50          |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 201            | aaaaaaaa                                                               | 50          |
    | aaaaaaaa                                                               | 201            | aaa                                                                    | 50          |
    | aaaaaaaa                                                               | 201            | aaaa                                                                   | 50          |
    | aaaaaaaa                                                               | 201            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  | 50          |
    | aaaaaaaa                                                               | 201            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50          |
    | valid_value                                                            | 201            | valid_value                                                            | valid_value |

@error @validation @post @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-correlation-id requerido
  Given path '/priorities'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  And request {}
  When method POST
  Then status 400

  Examples:
    | headerName       |
    | x-correlation-id |

@error @validation @invalid-type @post @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-correlation-id
  Given path '/priorities'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  And request {}
  When method POST
  Then status 400

  Examples:
    | headerName       | invalidValue |
    | x-correlation-id | invalid-uuid |

@error @validation @post @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-request-id requerido
  Given path '/priorities'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  And request {}
  When method POST
  Then status 400

  Examples:
    | headerName   |
    | x-request-id |

@error @validation @invalid-type @post @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-request-id
  Given path '/priorities'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  And request {}
  When method POST
  Then status 400

  Examples:
    | headerName   | invalidValue |
    | x-request-id | invalid-uuid |

@error @validation @post @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-transaction-id requerido
  Given path '/priorities'
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  And request {}
  When method POST
  Then status 400

  Examples:
    | headerName       |
    | x-transaction-id |

@error @validation @invalid-type @post @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-transaction-id
  Given path '/priorities'
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  And request {}
  When method POST
  Then status 400

  Examples:
    | headerName       | invalidValue |
    | x-transaction-id | invalid-uuid |

@error @validation @post @regression
Scenario Outline: Rechazar solicitud con datos inválidos
  # Tests que deben retornar Bad Request (400)
  Given path '/priorities'
  And headers configHeader
  And request <requestBody>
  When method POST
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.error == '#string'

  Examples:
    | name                                                                    | expectedStatus | description                                                             | idPriority  |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 12345       |
    | aa                                                                      | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |                                                                         | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |                                                                         | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    | 12345                                                                   | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aa                                                                      |             |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |             |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            |                                                                         |             |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            |                                                                         |             |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | 12345                                                                   |             |
    |                                                                         | 400            |                                                                         |             |
    | aa                                                                      | 400            | aaaaaaaa                                                                | 50          |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 400            | aaaaaaaa                                                                | 50          |
    | aaaaaaaa                                                                | 400            | aa                                                                      | 50          |
    | aaaaaaaa                                                                | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50          |
    | aa                                                                      | 400            | aaaaaaaa                                                                | 50          |
    | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 400            | aaaaaaaa                                                                | 50          |
    | aaaaaaaa                                                                | 400            | aa                                                                      | 50          |
    | aaaaaaaa                                                                | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50          |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value                                                             | 400            | valid_value                                                             | valid_value |

@error @post @status409 @regression
Scenario Outline: Rechazar solicitud por conflicto de recursos
  # Tests que deben retornar 409 (409)
  Given path '/priorities'
  And headers configHeader
  And request <requestBody>
  When method POST
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }

  Examples:
    | expectedStatus |
    | 409            |