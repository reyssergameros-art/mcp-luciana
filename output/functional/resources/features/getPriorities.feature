@regression @api

Feature: Listar todas las prioridades

Background:
  Given url baseUrl
  * def configHeader = karate.call('classpath:karate-config.js').buildHeaders({})

@smoke @happy-path @regression
Scenario Outline: Obtener priorities exitosamente
  # Caso exitoso: obtener con parámetros válidos
  Given path '/priorities'
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'

  Examples:
    | expectedStatus |
    | 200            |
    | 200            |
    | 200            |

@error @validation @get @regression
Scenario Outline: Rechazar solicitud cuando falta header requerido
  # Tests para validar x-correlation-id requerido
  Given path '/priorities'
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
  Given path '/priorities'
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
  Given path '/priorities'
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
  Given path '/priorities'
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
  Given path '/priorities'
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
  Given path '/priorities'
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
  Given path '/priorities'
  And headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match response == '#object'
  And match response contains any { error: '#present', message: '#present', code: '#present' }
  And match response.error == '#string'

  Examples:
    | expectedStatus |
    | 400            |
    | 400            |
    | 400            |
    | 400            |
    | 400            |
    | 400            |
    | 400            |
    | 400            |