@regression @api

Feature: Actualizar prioridad

Background:
  Given url baseUrl
  * def configHeader = karate.call('classpath:karate-config.js').buildHeaders({})

@smoke @happy-path @regression
Scenario Outline: Actualizar priorities exitosamente
  # Caso exitoso: actualizar con parámetros válidos
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  And request <requestBody>
  When method PUT
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'

  Examples:
    | id          | name                                                                   | expectedStatus | description                                                            | idPriority  |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                   | 200            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                   |             |
    | 1           |                                                                        | 200            |                                                                        |             |
    | 50          | aaa                                                                    | 201            | aaaaaaaa                                                               | 50          |
    | 50          | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 201            | aaaaaaaa                                                               | 50          |
    | 50          | aaaaaaaa                                                               | 201            | aaa                                                                    | 50          |
    | 50          | aaaaaaaa                                                               | 201            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50          |
    | 50          | aaa                                                                    | 201            | aaaaaaaa                                                               | 50          |
    | 50          | aaaa                                                                   | 201            | aaaaaaaa                                                               | 50          |
    | 50          | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  | 201            | aaaaaaaa                                                               | 50          |
    | 50          | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 201            | aaaaaaaa                                                               | 50          |
    | 50          | aaaaaaaa                                                               | 201            | aaa                                                                    | 50          |
    | 50          | aaaaaaaa                                                               | 201            | aaaa                                                                   | 50          |
    | 50          | aaaaaaaa                                                               | 201            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  | 50          |
    | 50          | aaaaaaaa                                                               | 201            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50          |
    | valid_value | valid_value                                                            | 200            | valid_value                                                            | valid_value |

@error @validation @put @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-correlation-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  And request {}
  When method PUT
  Then status 400

  Examples:
    | headerName       |
    | x-correlation-id |

@error @validation @invalid-type @put @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-correlation-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  And request {}
  When method PUT
  Then status 400

  Examples:
    | headerName       | invalidValue |
    | x-correlation-id | invalid-uuid |

@error @validation @put @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-request-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  And request {}
  When method PUT
  Then status 400

  Examples:
    | headerName   |
    | x-request-id |

@error @validation @invalid-type @put @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-request-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  And request {}
  When method PUT
  Then status 400

  Examples:
    | headerName   | invalidValue |
    | x-request-id | invalid-uuid |

@error @validation @put @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-transaction-id requerido
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * remove headers.<headerName>
  And headers headers
  And request {}
  When method PUT
  Then status 400

  Examples:
    | headerName       |
    | x-transaction-id |

@error @validation @invalid-type @put @regression
Scenario Outline: Rechazar solicitud cuando header tiene tipo incorrecto
  # Tests para validar tipo de x-transaction-id
  * def id = '<id>'
  Given path '/priorities/', id
  * def headers = configHeader
  * headers['<headerName>'] = <invalidValue>
  And headers headers
  And request {}
  When method PUT
  Then status 400

  Examples:
    | headerName       | invalidValue |
    | x-transaction-id | invalid-uuid |

@error @validation @put @regression
Scenario Outline: Rechazar solicitud con datos inválidos
  # Tests que deben retornar Bad Request (400)
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  And request <requestBody>
  When method PUT
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.error == '#string'

  Examples:
    | id          | name                                                                    | expectedStatus | description                                                             | idPriority  |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    | 12345       | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 12345       |
    |             | aa                                                                      | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |             |                                                                         | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |             |                                                                         | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |             | 12345                                                                   | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |             |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aa                                                                      |             |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |             |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            |                                                                         |             |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            |                                                                         |             |
    |             | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 400            | 12345                                                                   |             |
    | 1           |                                                                         | 400            |                                                                         |             |
    | 50          | aa                                                                      | 400            | aaaaaaaa                                                                | 50          |
    | 50          | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 400            | aaaaaaaa                                                                | 50          |
    | 50          | aaaaaaaa                                                                | 400            | aa                                                                      | 50          |
    | 50          | aaaaaaaa                                                                | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50          |
    | 50          | aa                                                                      | 400            | aaaaaaaa                                                                | 50          |
    | 50          | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 400            | aaaaaaaa                                                                | 50          |
    | 50          | aaaaaaaa                                                                | 400            | aa                                                                      | 50          |
    | 50          | aaaaaaaa                                                                | 400            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50          |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |
    | valid_value | valid_value                                                             | 400            | valid_value                                                             | valid_value |

@error @not-found @put @status404 @regression
Scenario Outline: Rechazar solicitud de recurso inexistente
  # Tests que deben retornar Not Found (404)
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  And request <requestBody>
  When method PUT
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.message == '#string'

  Examples:
    | id     | expectedStatus |
    | 999999 | 404            |

@error @put @status409 @regression
Scenario Outline: Rechazar solicitud por conflicto de recursos
  # Tests que deben retornar 409 (409)
  * def id = '<id>'
  Given path '/priorities/', id
  And headers configHeader
  And request <requestBody>
  When method PUT
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }

  Examples:
    | id | expectedStatus |
    | 1  | 409            |