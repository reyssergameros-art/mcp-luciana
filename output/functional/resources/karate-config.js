function fn() {
  var env = karate.env; // get system property 'karate.env'
  karate.log('karate.env system property was:', env);
  
  if (!env) {
    env = 'dev';
  }
  
  var config = {
    baseUrl: 'https://virtserver.swaggerhub.com/PacificoSegurosPeru/API-SP-DocumentosPolizaSalud/1.0.0',
    timeout: 30000,
    retry: 0
  };
  
  // Helper function to generate UUIDs
  config.generateUUID = function() {
    return java.util.UUID.randomUUID() + '';
  };
  
  // Default headers configuration for all endpoints
  config.headersDefaultEndpoint = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  
  // Legacy common headers function (for backward compatibility)
  config.getCommonHeaders = function() {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  };
  
  // Environment specific configuration
  if (env === 'dev') {
    config.baseUrl = 'https://dev-virtserver.swaggerhub.com';
  }
  else if (env === 'qa') {
    config.baseUrl = 'https://qa-virtserver.swaggerhub.com';
  }
  else if (env === 'prod') {
    config.baseUrl = 'https://virtserver.swaggerhub.com';
  }
  
  karate.configure('connectTimeout', config.timeout);
  karate.configure('readTimeout', config.timeout);
  karate.configure('retry', { count: config.retry, interval: 5000 });
  
  return config;
}