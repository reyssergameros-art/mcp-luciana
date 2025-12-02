@regression @delete

Feature: Eliminar prioridad

Background:
  * def randomXCorrelationId = java.util.UUID.randomUUID().toString()
  * def randomXRequestId = java.util.UUID.randomUUID().toString()
  * def randomXTransactionId = java.util.UUID.randomUUID().toString()
  * def id = karate.get('id', '1')
  Given url baseUrl
  And path '/priorities/{id}'
  * def configHeader = headersDefaultEndpoint
  * configHeader['x-transaction-id'] = randomXTransactionId
  * configHeader['x-correlation-id'] = randomXCorrelationId
  * configHeader['x-request-id'] = randomXRequestId

@delete @happyPath @smoke
Scenario Outline: Verificar éxito en DELETE con datos válidos
  # Tests con datos válidos que deben ser exitosos
  * def id = '<id>'
  * headers configHeader
  When method DELETE
  Then status <expectedStatus>
  And match response != null
  And match responseType == 'json'

  Examples:
    | testName                                   | expectedStatus | priority |
    | DELETE /priorities/{id} - All Valid Inputs | 204            | high     |

@regression @delete @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-correlation-id
  * def id = '<id>'
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  When method DELETE
  Then status 400

  Examples:
    | action | condition                       | headerName       |
    | null   | tiene valor inválido (formato)  | x-correlation-id |
    | null   | tiene valor inválido (formato)  | x-correlation-id |
    | null   | tiene valor inválido (formato)  | x-correlation-id |
    | null   | tiene valor inválido (longitud) | x-correlation-id |
    | null   | tiene valor inválido (longitud) | x-correlation-id |
    | remove | no está presente                | x-correlation-id |
    | remove | no está presente                | x-correlation-id |
    | null   | tiene valor inválido (tipo)     | x-correlation-id |

@regression @delete @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-request-id
  * def id = '<id>'
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  When method DELETE
  Then status 400

  Examples:
    | action | condition                       | headerName   |
    | null   | tiene valor inválido (formato)  | x-request-id |
    | null   | tiene valor inválido (formato)  | x-request-id |
    | null   | tiene valor inválido (formato)  | x-request-id |
    | null   | tiene valor inválido (longitud) | x-request-id |
    | null   | tiene valor inválido (longitud) | x-request-id |
    | remove | no está presente                | x-request-id |
    | remove | no está presente                | x-request-id |
    | null   | tiene valor inválido (tipo)     | x-request-id |

@regression @delete @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-transaction-id
  * def id = '<id>'
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  When method DELETE
  Then status 400

  Examples:
    | action | condition                       | headerName       |
    | null   | tiene valor inválido (formato)  | x-transaction-id |
    | null   | tiene valor inválido (formato)  | x-transaction-id |
    | null   | tiene valor inválido (formato)  | x-transaction-id |
    | null   | tiene valor inválido (longitud) | x-transaction-id |
    | null   | tiene valor inválido (longitud) | x-transaction-id |
    | remove | no está presente                | x-transaction-id |
    | remove | no está presente                | x-transaction-id |
    | null   | tiene valor inválido (tipo)     | x-transaction-id |

@regression @delete @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request con datos inválidos
  # Tests con datos inválidos que deben retornar Bad Request
  * def id = '<id>'
  * headers configHeader
  When method DELETE
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | id    | testName                                        | expectedStatus | priority |
    |       | DELETE /priorities/{id} - Invalid id (required) | 400            | high     |
    |       | DELETE /priorities/{id} - Invalid id (required) | 400            | high     |
    | 12345 | DELETE /priorities/{id} - Invalid id (type)     | 400            | low      |