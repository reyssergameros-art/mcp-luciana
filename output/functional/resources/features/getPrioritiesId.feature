@regression @get

Feature: Obtener prioridad por ID

Background:
  * url baseUrl
  * def commonHeaders = getCommonHeaders()
  * configure headers = commonHeaders
  # Path parameters will be set in scenarios

@positive @smoke @get
Scenario Outline: Successful GET requests
  # Tests with valid inputs that should succeed
  Given path '/priorities/{id}'
  And param id = <id>
  And header x-correlation-id = <xCorrelationId>
  And header x-request-id = <xRequestId>
  And header x-transaction-id = <xTransactionId>
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match responseType == 'json'

  Examples:
    | testId                               | testName                                | expectedStatus | expectedError | priority | x-correlation-id                     | x-request-id                         | x-transaction-id                     |
    | EPGETprioritiesidvalid_all20251128_1 | GET /priorities/{id} - All Valid Inputs | 200            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000 | 550e8400-e29b-41d4-a716-446655440000 | 550e8400-e29b-41d4-a716-446655440000 |

@negative @status400 @get @regression
Scenario Outline: GET requests returning 400
  # Tests that should fail with HTTP 400
  Given path '/priorities/{id}'
  And param id = <id>
  And header x-correlation-id = <xCorrelationId>
  And header x-request-id = <xRequestId>
  And header x-transaction-id = <xTransactionId>
  When method GET
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | testId                                                        | testName                                                   | expectedStatus | expectedError | priority | x-correlation-id                           | x-request-id                               | x-transaction-id                           |
    | EPGETprioritiesidinvalid_x-correlation-id_format20251128_2    | GET /priorities/{id} - Invalid x-correlation-id (format)   | 400            | N/A           | high     | invalid-uuid                               | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-correlation-id_format20251128_3    | GET /priorities/{id} - Invalid x-correlation-id (format)   | 400            | N/A           | high     | 123                                        | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-correlation-id_format20251128_4    | GET /priorities/{id} - Invalid x-correlation-id (format)   | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-correlation-id_length20251128_5    | GET /priorities/{id} - Invalid x-correlation-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716                    | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-correlation-id_length20251128_6    | GET /priorities/{id} - Invalid x-correlation-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000-extra | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-correlation-id_required20251128_7  | GET /priorities/{id} - Invalid x-correlation-id (required) | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-correlation-id_required20251128_8  | GET /priorities/{id} - Invalid x-correlation-id (required) | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-correlation-id_type20251128_9      | GET /priorities/{id} - Invalid x-correlation-id (type)     | 400            | N/A           | low      | 12345                                      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-request-id_format20251128_10       | GET /priorities/{id} - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | invalid-uuid                               | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-request-id_format20251128_11       | GET /priorities/{id} - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 123                                        | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-request-id_format20251128_12       | GET /priorities/{id} - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-request-id_length20251128_13       | GET /priorities/{id} - Invalid x-request-id (length)       | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716                    | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-request-id_length20251128_14       | GET /priorities/{id} - Invalid x-request-id (length)       | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000-extra | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-request-id_required20251128_15     | GET /priorities/{id} - Invalid x-request-id (required)     | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-request-id_required20251128_16     | GET /priorities/{id} - Invalid x-request-id (required)     | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-request-id_type20251128_17         | GET /priorities/{id} - Invalid x-request-id (type)         | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 12345                                      | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_x-transaction-id_format20251128_18   | GET /priorities/{id} - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | invalid-uuid                               |
    | EPGETprioritiesidinvalid_x-transaction-id_format20251128_19   | GET /priorities/{id} - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 123                                        |
    | EPGETprioritiesidinvalid_x-transaction-id_format20251128_20   | GET /priorities/{id} - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesidinvalid_x-transaction-id_length20251128_21   | GET /priorities/{id} - Invalid x-transaction-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716                    |
    | EPGETprioritiesidinvalid_x-transaction-id_length20251128_22   | GET /priorities/{id} - Invalid x-transaction-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000-extra |
    | EPGETprioritiesidinvalid_x-transaction-id_required20251128_23 | GET /priorities/{id} - Invalid x-transaction-id (required) | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesidinvalid_x-transaction-id_required20251128_24 | GET /priorities/{id} - Invalid x-transaction-id (required) | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesidinvalid_x-transaction-id_type20251128_25     | GET /priorities/{id} - Invalid x-transaction-id (type)     | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 12345                                      |
    | EPGETprioritiesidinvalid_id_required20251128_26               | GET /priorities/{id} - Invalid id (required)               | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_id_required20251128_27               | GET /priorities/{id} - Invalid id (required)               | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesidinvalid_id_type20251128_28                   | GET /priorities/{id} - Invalid id (type)                   | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |