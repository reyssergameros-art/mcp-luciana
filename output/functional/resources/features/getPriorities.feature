@regression @get

Feature: Listar todas las prioridades

Background:
  * def randomXCorrelationId = java.util.UUID.randomUUID().toString()
  * def randomXRequestId = java.util.UUID.randomUUID().toString()
  * def randomXTransactionId = java.util.UUID.randomUUID().toString()
  Given url baseUrl
  And path '/priorities'
  * def configHeader = headersDefaultEndpoint
  * configHeader['x-transaction-id'] = randomXTransactionId
  * configHeader['x-correlation-id'] = randomXCorrelationId
  * configHeader['x-request-id'] = randomXRequestId

@get @happyPath @smoke
Scenario Outline: Verificar éxito en GET con datos válidos
  # Tests con datos válidos que deben ser exitosos
  * headers configHeader
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match responseType == 'json'

  Examples:
    | testName                           | expectedStatus | priority |
    | GET /priorities - All Valid Inputs | 200            | high     |

@regression @get @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-correlation-id
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  When method GET
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

@regression @get @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-request-id
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  When method GET
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

@regression @get @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-transaction-id
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  When method GET
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