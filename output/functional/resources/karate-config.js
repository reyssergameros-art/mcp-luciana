function fn() {
  var env = karate.env; // get system property 'karate.env'
  karate.log('karate.env system property was:', env);
  
  if (!env) {
    env = 'dev';
  }
  
  var config = {
    baseUrl: 'http://localhost:8080',
    timeout: 30000,
    retry: 0
  };
  
  // Common headers
  config.headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  
  // Helper functions
  config.generateUUID = function() {
    return java.util.UUID.randomUUID() + '';
  };
  
  config.getCommonHeaders = function() {
    return {
      'x-correlation-id': config.generateUUID(),
      'x-request-id': config.generateUUID(),
      'x-transaction-id': config.generateUUID(),
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  };
  
  // Environment specific configuration
  if (env === 'dev') {
    config.baseUrl = 'http://localhost:8080';
  }
  else if (env === 'qa') {
    config.baseUrl = 'https://qa.example.com';
  }
  else if (env === 'prod') {
    config.baseUrl = 'https://api.example.com';
  }
  
  karate.configure('connectTimeout', config.timeout);
  karate.configure('readTimeout', config.timeout);
  karate.configure('retry', { count: config.retry, interval: 5000 });
  
  return config;
}