@regression @post

Feature: Crear nueva prioridad

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

@happyPath @post @smoke
Scenario Outline: Verificar éxito en POST con datos válidos
  # Tests con datos válidos que deben ser exitosos
  * headers configHeader
  And request <requestBody>
  When method POST
  Then status <expectedStatus>
  And match response != null
  And match responseType == 'json'

  Examples:
    | testName                                         | expectedStatus | priority | description                                                            | idPriority | name                                                                   |
    | POST /priorities - All Valid Inputs              | 201            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                   |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                   |
    | POST /priorities - name = boundaryMinimum        | 201            | medium   | aaaaaaaa                                                               | 50         | aaa                                                                    |
    | POST /priorities - name = boundaryMaximum        | 201            | medium   | aaaaaaaa                                                               | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | POST /priorities - description = boundaryMinimum | 201            | medium   | aaa                                                                    | 50         | aaaaaaaa                                                               |
    | POST /priorities - description = boundaryMaximum | 201            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50         | aaaaaaaa                                                               |
    | POST /priorities - name = boundaryMinimum        | 201            | medium   | aaaaaaaa                                                               | 50         | aaa                                                                    |
    | POST /priorities - name = aboveMin               | 201            | medium   | aaaaaaaa                                                               | 50         | aaaa                                                                   |
    | POST /priorities - name = belowMax               | 201            | medium   | aaaaaaaa                                                               | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  |
    | POST /priorities - name = boundaryMaximum        | 201            | medium   | aaaaaaaa                                                               | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | POST /priorities - description = boundaryMinimum | 201            | medium   | aaa                                                                    | 50         | aaaaaaaa                                                               |
    | POST /priorities - description = aboveMin        | 201            | medium   | aaaa                                                                   | 50         | aaaaaaaa                                                               |
    | POST /priorities - description = belowMax        | 201            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  | 50         | aaaaaaaa                                                               |
    | POST /priorities - description = boundaryMaximum | 201            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50         | aaaaaaaa                                                               |

@regression @post @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-correlation-id
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  And request {}
  When method POST
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

@regression @post @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-request-id
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  And request {}
  When method POST
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

@regression @post @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-transaction-id
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  And request {}
  When method POST
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

@regression @post @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request con datos inválidos
  # Tests con datos inválidos que deben retornar Bad Request
  * headers configHeader
  And request <requestBody>
  When method POST
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | testName                                          | expectedStatus | priority | description                                                             | idPriority | name                                                                    |
    | POST /priorities - Invalid idPriority (type)      | 400            | low      | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 12345      | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    | POST /priorities - Invalid name (length)          | 400            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | aa                                                                      |
    | POST /priorities - Invalid name (length)          | 400            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | POST /priorities - Invalid name (required)        | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            |                                                                         |
    | POST /priorities - Invalid name (required)        | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            |                                                                         |
    | POST /priorities - Invalid name (type)            | 400            | low      | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | 12345                                                                   |
    | POST /priorities - Invalid description (length)   | 400            | medium   | aa                                                                      |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    | POST /priorities - Invalid description (length)   | 400            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    | POST /priorities - Invalid description (required) | 400            | high     |                                                                         |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    | POST /priorities - Invalid description (required) | 400            | high     |                                                                         |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    | POST /priorities - Invalid description (type)     | 400            | low      | 12345                                                                   |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    | POST /priorities - name = belowMin                | 400            | high     | aaaaaaaa                                                                | 50         | aa                                                                      |
    | POST /priorities - name = aboveMax                | 400            | high     | aaaaaaaa                                                                | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | POST /priorities - description = belowMin         | 400            | high     | aa                                                                      | 50         | aaaaaaaa                                                                |
    | POST /priorities - description = aboveMax         | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50         | aaaaaaaa                                                                |
    | POST /priorities - name = belowMin                | 400            | high     | aaaaaaaa                                                                | 50         | aa                                                                      |
    | POST /priorities - name = aboveMax                | 400            | high     | aaaaaaaa                                                                | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | POST /priorities - description = belowMin         | 400            | high     | aa                                                                      | 50         | aaaaaaaa                                                                |
    | POST /priorities - description = aboveMax         | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50         | aaaaaaaa                                                                |