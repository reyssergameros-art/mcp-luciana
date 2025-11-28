@regression @get

Feature: Listar todas las prioridades

Background:
  * url baseUrl
  * def commonHeaders = getCommonHeaders()
  * configure headers = commonHeaders

@get @smoke @positive
Scenario Outline: Successful GET requests
  # Tests with valid inputs that should succeed
  Given path '/priorities'
  And header x-correlation-id = <xCorrelationId>
  And header x-request-id = <xRequestId>
  And header x-transaction-id = <xTransactionId>
  When method GET
  Then status <expectedStatus>
  And match response != null
  And match responseType == 'json'

  Examples:
    | testId                              | testName                           | expectedStatus | expectedError | priority | x-correlation-id                     | x-request-id                         | x-transaction-id                     |
    | EPGETprioritiesvalid_all20251128_96 | GET /priorities - All Valid Inputs | 200            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000 | 550e8400-e29b-41d4-a716-446655440000 | 550e8400-e29b-41d4-a716-446655440000 |

@status400 @get @negative @regression
Scenario Outline: GET requests returning 400
  # Tests that should fail with HTTP 400
  Given path '/priorities'
  And header x-correlation-id = <xCorrelationId>
  And header x-request-id = <xRequestId>
  And header x-transaction-id = <xTransactionId>
  When method GET
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | testId                                                       | testName                                              | expectedStatus | expectedError | priority | x-correlation-id                           | x-request-id                               | x-transaction-id                           |
    | EPGETprioritiesinvalid_x-correlation-id_format20251128_97    | GET /priorities - Invalid x-correlation-id (format)   | 400            | N/A           | high     | invalid-uuid                               | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_format20251128_98    | GET /priorities - Invalid x-correlation-id (format)   | 400            | N/A           | high     | 123                                        | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_format20251128_99    | GET /priorities - Invalid x-correlation-id (format)   | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_length20251128_100   | GET /priorities - Invalid x-correlation-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716                    | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_length20251128_101   | GET /priorities - Invalid x-correlation-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000-extra | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_required20251128_102 | GET /priorities - Invalid x-correlation-id (required) | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_required20251128_103 | GET /priorities - Invalid x-correlation-id (required) | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_type20251128_104     | GET /priorities - Invalid x-correlation-id (type)     | 400            | N/A           | low      | 12345                                      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_format20251128_105       | GET /priorities - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | invalid-uuid                               | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_format20251128_106       | GET /priorities - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 123                                        | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_format20251128_107       | GET /priorities - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_length20251128_108       | GET /priorities - Invalid x-request-id (length)       | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716                    | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_length20251128_109       | GET /priorities - Invalid x-request-id (length)       | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000-extra | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_required20251128_110     | GET /priorities - Invalid x-request-id (required)     | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_required20251128_111     | GET /priorities - Invalid x-request-id (required)     | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_type20251128_112         | GET /priorities - Invalid x-request-id (type)         | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 12345                                      | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-transaction-id_format20251128_113   | GET /priorities - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | invalid-uuid                               |
    | EPGETprioritiesinvalid_x-transaction-id_format20251128_114   | GET /priorities - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 123                                        |
    | EPGETprioritiesinvalid_x-transaction-id_format20251128_115   | GET /priorities - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesinvalid_x-transaction-id_length20251128_116   | GET /priorities - Invalid x-transaction-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716                    |
    | EPGETprioritiesinvalid_x-transaction-id_length20251128_117   | GET /priorities - Invalid x-transaction-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000-extra |
    | EPGETprioritiesinvalid_x-transaction-id_required20251128_118 | GET /priorities - Invalid x-transaction-id (required) | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesinvalid_x-transaction-id_required20251128_119 | GET /priorities - Invalid x-transaction-id (required) | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesinvalid_x-transaction-id_type20251128_120     | GET /priorities - Invalid x-transaction-id (type)     | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 12345                                      |