@regression @delete

Feature: DELETE Priorities Id

Background:
  * url baseUrl
  * def commonHeaders = getCommonHeaders()
  * configure headers = commonHeaders
  # Path parameters will be set in scenarios

@delete @smoke @positive
Scenario Outline: Successful DELETE requests
  # Tests with valid inputs that should succeed
  Given path '/priorities/{id}'
  And param id = <id>
  And header x-correlation-id = <xCorrelationId>
  And header x-request-id = <xRequestId>
  And header x-transaction-id = <xTransactionId>
  When method DELETE
  Then status <expectedStatus>
  And match response != null
  And match responseType == 'json'

  Examples:
    | testId                                   | testName                                   | expectedStatus | expectedError | priority | x-correlation-id                     | x-request-id                         | x-transaction-id                     |
    | EPDELETEprioritiesidvalid_all20251126_68 | DELETE /priorities/{id} - All Valid Inputs | 204            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000 | 550e8400-e29b-41d4-a716-446655440000 | 550e8400-e29b-41d4-a716-446655440000 |

@delete @regression @negative @status400
Scenario Outline: DELETE requests returning 400
  # Tests that should fail with HTTP 400
  Given path '/priorities/{id}'
  And param id = <id>
  And header x-correlation-id = <xCorrelationId>
  And header x-request-id = <xRequestId>
  And header x-transaction-id = <xTransactionId>
  When method DELETE
  Then status <expectedStatus>
  And match response.error != null

  Examples:
    | testId                                                           | testName                                                      | expectedStatus | expectedError | priority | x-correlation-id                           | x-request-id                               | x-transaction-id                           |
    | EPDELETEprioritiesidinvalid_x-correlation-id_format20251126_69   | DELETE /priorities/{id} - Invalid x-correlation-id (format)   | 400            | N/A           | high     | invalid-uuid                               | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-correlation-id_format20251126_70   | DELETE /priorities/{id} - Invalid x-correlation-id (format)   | 400            | N/A           | high     | 123                                        | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-correlation-id_format20251126_71   | DELETE /priorities/{id} - Invalid x-correlation-id (format)   | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-correlation-id_length20251126_72   | DELETE /priorities/{id} - Invalid x-correlation-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716                    | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-correlation-id_length20251126_73   | DELETE /priorities/{id} - Invalid x-correlation-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000-extra | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-correlation-id_required20251126_74 | DELETE /priorities/{id} - Invalid x-correlation-id (required) | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-correlation-id_required20251126_75 | DELETE /priorities/{id} - Invalid x-correlation-id (required) | 400            | N/A           | high     |                                            | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-correlation-id_type20251126_76     | DELETE /priorities/{id} - Invalid x-correlation-id (type)     | 400            | N/A           | low      | 12345                                      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-request-id_format20251126_77       | DELETE /priorities/{id} - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | invalid-uuid                               | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-request-id_format20251126_78       | DELETE /priorities/{id} - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 123                                        | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-request-id_format20251126_79       | DELETE /priorities/{id} - Invalid x-request-id (format)       | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-request-id_length20251126_80       | DELETE /priorities/{id} - Invalid x-request-id (length)       | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716                    | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-request-id_length20251126_81       | DELETE /priorities/{id} - Invalid x-request-id (length)       | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000-extra | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-request-id_required20251126_82     | DELETE /priorities/{id} - Invalid x-request-id (required)     | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-request-id_required20251126_83     | DELETE /priorities/{id} - Invalid x-request-id (required)     | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       |                                            | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-request-id_type20251126_84         | DELETE /priorities/{id} - Invalid x-request-id (type)         | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 12345                                      | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_x-transaction-id_format20251126_85   | DELETE /priorities/{id} - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | invalid-uuid                               |
    | EPDELETEprioritiesidinvalid_x-transaction-id_format20251126_86   | DELETE /priorities/{id} - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 123                                        |
    | EPDELETEprioritiesidinvalid_x-transaction-id_format20251126_87   | DELETE /priorities/{id} - Invalid x-transaction-id (format)   | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPDELETEprioritiesidinvalid_x-transaction-id_length20251126_88   | DELETE /priorities/{id} - Invalid x-transaction-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716                    |
    | EPDELETEprioritiesidinvalid_x-transaction-id_length20251126_89   | DELETE /priorities/{id} - Invalid x-transaction-id (length)   | 400            | N/A           | medium   | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000-extra |
    | EPDELETEprioritiesidinvalid_x-transaction-id_required20251126_90 | DELETE /priorities/{id} - Invalid x-transaction-id (required) | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPDELETEprioritiesidinvalid_x-transaction-id_required20251126_91 | DELETE /priorities/{id} - Invalid x-transaction-id (required) | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |                                            |
    | EPDELETEprioritiesidinvalid_x-transaction-id_type20251126_92     | DELETE /priorities/{id} - Invalid x-transaction-id (type)     | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 12345                                      |
    | EPDELETEprioritiesidinvalid_id_required20251126_93               | DELETE /priorities/{id} - Invalid id (required)               | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_id_required20251126_94               | DELETE /priorities/{id} - Invalid id (required)               | 400            | N/A           | high     | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |
    | EPDELETEprioritiesidinvalid_id_type20251126_95                   | DELETE /priorities/{id} - Invalid id (type)                   | 400            | N/A           | low      | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       | 550e8400-e29b-41d4-a716-446655440000       |