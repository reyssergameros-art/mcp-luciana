@regression @get

Feature: Listar todas las prioridades

Background:
  * url baseUrl
  * def commonHeaders = getCommonHeaders()
  * configure headers = commonHeaders

@positive @get @smoke
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
    | EPGETprioritiesvalid_all20251126_96 | GET /priorities - All Valid Inputs | 200            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000 | 550e8400-e29b-41d4-a716-446655440000 | 550e8400-e29b-41d4-a716-446655440000 |

@negative @get @status400 @regression
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
    | EPGETprioritiesinvalid_x-correlation-id_format20251126_97    | GET /priorities - Invalid x-correlation-id (format)   | 400            | N/A           | high     | invalid-uuid                               | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_format20251126_98    | GET /priorities - Invalid x-correlation-id (format)   | 400            | N/A           | high     | 123                                        | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_format20251126_99    | GET /priorities - Invalid x-correlation-id (format)   | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_length20251126_100   | GET /priorities - Invalid x-correlation-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716                    | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_length20251126_101   | GET /priorities - Invalid x-correlation-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000-extra | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_required20251126_102 | GET /priorities - Invalid x-correlation-id (required) | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_required20251126_103 | GET /priorities - Invalid x-correlation-id (required) | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-correlation-id_type20251126_104     | GET /priorities - Invalid x-correlation-id (type)     | 400            | N/A           | low      | 12345                                      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_format20251126_105       | GET /priorities - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | invalid-uuid                               | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_format20251126_106       | GET /priorities - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 123                                        | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_format20251126_107       | GET /priorities - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_length20251126_108       | GET /priorities - Invalid x-request-id (length)       | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716                    | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_length20251126_109       | GET /priorities - Invalid x-request-id (length)       | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000-extra | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_required20251126_110     | GET /priorities - Invalid x-request-id (required)     | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_required20251126_111     | GET /priorities - Invalid x-request-id (required)     | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-request-id_type20251126_112         | GET /priorities - Invalid x-request-id (type)         | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 12345                                      | 550e8400-e29b-41d4-a716-446655440000       |
    | EPGETprioritiesinvalid_x-transaction-id_format20251126_113   | GET /priorities - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | invalid-uuid                               |
    | EPGETprioritiesinvalid_x-transaction-id_format20251126_114   | GET /priorities - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 123                                        |
    | EPGETprioritiesinvalid_x-transaction-id_format20251126_115   | GET /priorities - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesinvalid_x-transaction-id_length20251126_116   | GET /priorities - Invalid x-transaction-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716                    |
    | EPGETprioritiesinvalid_x-transaction-id_length20251126_117   | GET /priorities - Invalid x-transaction-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000-extra |
    | EPGETprioritiesinvalid_x-transaction-id_required20251126_118 | GET /priorities - Invalid x-transaction-id (required) | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesinvalid_x-transaction-id_required20251126_119 | GET /priorities - Invalid x-transaction-id (required) | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPGETprioritiesinvalid_x-transaction-id_type20251126_120     | GET /priorities - Invalid x-transaction-id (type)     | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 12345                                      |