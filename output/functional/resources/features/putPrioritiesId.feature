@regression @put

Feature: Actualizar prioridad

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

@happyPath @smoke @put
Scenario Outline: Verificar éxito en PUT con datos válidos
  # Tests con datos válidos que deben ser exitosos
  * def id = '<id>'
  * headers configHeader
  And request <requestBody>
  When method PUT
  Then status <expectedStatus>
  And match response != null
  And match responseType == 'json'

  Examples:
    | id | testName                                             | expectedStatus | priority | description                                                            | idPriority | name                                                                   |
    |    | PUT /priorities/{id} - All Valid Inputs              | 200            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                   |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                   |
    | 50 | PUT /priorities/{id} - name = boundaryMinimum        | 201            | medium   | aaaaaaaa                                                               | 50         | aaa                                                                    |
    | 50 | PUT /priorities/{id} - name = boundaryMaximum        | 201            | medium   | aaaaaaaa                                                               | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | 50 | PUT /priorities/{id} - description = boundaryMinimum | 201            | medium   | aaa                                                                    | 50         | aaaaaaaa                                                               |
    | 50 | PUT /priorities/{id} - description = boundaryMaximum | 201            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50         | aaaaaaaa                                                               |
    | 50 | PUT /priorities/{id} - name = boundaryMinimum        | 201            | medium   | aaaaaaaa                                                               | 50         | aaa                                                                    |
    | 50 | PUT /priorities/{id} - name = aboveMin               | 201            | medium   | aaaaaaaa                                                               | 50         | aaaa                                                                   |
    | 50 | PUT /priorities/{id} - name = belowMax               | 201            | medium   | aaaaaaaa                                                               | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  |
    | 50 | PUT /priorities/{id} - name = boundaryMaximum        | 201            | medium   | aaaaaaaa                                                               | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | 50 | PUT /priorities/{id} - description = boundaryMinimum | 201            | medium   | aaa                                                                    | 50         | aaaaaaaa                                                               |
    | 50 | PUT /priorities/{id} - description = aboveMin        | 201            | medium   | aaaa                                                                   | 50         | aaaaaaaa                                                               |
    | 50 | PUT /priorities/{id} - description = belowMax        | 201            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  | 50         | aaaaaaaa                                                               |
    | 50 | PUT /priorities/{id} - description = boundaryMaximum | 201            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50         | aaaaaaaa                                                               |

@regression @put @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-correlation-id
  * def id = '<id>'
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  And request {}
  When method PUT
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

@regression @put @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-request-id
  * def id = '<id>'
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  And request {}
  When method PUT
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

@regression @put @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request cuando <headerName> <condition>
  # Tests para validar x-transaction-id
  * def id = '<id>'
  * if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')
  * if ('<action>' == 'null') configHeader['<headerName>'] = null
  * headers configHeader
  And request {}
  When method PUT
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

@regression @put @negativeTest
Scenario Outline: Verificar que el servicio responda Bad Request con datos inválidos
  # Tests con datos inválidos que deben retornar Bad Request
  * def id = '<id>'
  * headers configHeader
  And request <requestBody>
  When method PUT
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | id    | testName                                              | expectedStatus | priority | description                                                             | idPriority | name                                                                    |
    |       | PUT /priorities/{id} - Invalid id (required)          | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    |       | PUT /priorities/{id} - Invalid id (required)          | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    | 12345 | PUT /priorities/{id} - Invalid id (type)              | 400            | low      | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    |       | PUT /priorities/{id} - Invalid idPriority (type)      | 400            | low      | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    | 12345      | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    |       | PUT /priorities/{id} - Invalid name (length)          | 400            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | aa                                                                      |
    |       | PUT /priorities/{id} - Invalid name (length)          | 400            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    |       | PUT /priorities/{id} - Invalid name (required)        | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            |                                                                         |
    |       | PUT /priorities/{id} - Invalid name (required)        | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            |                                                                         |
    |       | PUT /priorities/{id} - Invalid name (type)            | 400            | low      | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |            | 12345                                                                   |
    |       | PUT /priorities/{id} - Invalid description (length)   | 400            | medium   | aa                                                                      |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    |       | PUT /priorities/{id} - Invalid description (length)   | 400            | medium   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    |       | PUT /priorities/{id} - Invalid description (required) | 400            | high     |                                                                         |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    |       | PUT /priorities/{id} - Invalid description (required) | 400            | high     |                                                                         |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    |       | PUT /priorities/{id} - Invalid description (type)     | 400            | low      | 12345                                                                   |            | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                                    |
    | 50    | PUT /priorities/{id} - name = belowMin                | 400            | high     | aaaaaaaa                                                                | 50         | aa                                                                      |
    | 50    | PUT /priorities/{id} - name = aboveMax                | 400            | high     | aaaaaaaa                                                                | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | 50    | PUT /priorities/{id} - description = belowMin         | 400            | high     | aa                                                                      | 50         | aaaaaaaa                                                                |
    | 50    | PUT /priorities/{id} - description = aboveMax         | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50         | aaaaaaaa                                                                |
    | 50    | PUT /priorities/{id} - name = belowMin                | 400            | high     | aaaaaaaa                                                                | 50         | aa                                                                      |
    | 50    | PUT /priorities/{id} - name = aboveMax                | 400            | high     | aaaaaaaa                                                                | 50         | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
    | 50    | PUT /priorities/{id} - description = belowMin         | 400            | high     | aa                                                                      | 50         | aaaaaaaa                                                                |
    | 50    | PUT /priorities/{id} - description = aboveMax         | 400            | high     | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 50         | aaaaaaaa                                                                |