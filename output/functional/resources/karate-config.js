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
  
  // Helper function to generate UUIDs using Karate native
  config.generateUUID = function() {
    return karate.uuid();
  };
  
  // Function to build request headers with automatic UUID generation
  config.buildHeaders = function(overrides) {
    overrides = overrides || {};
    var headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'x-correlation-id': config.generateUUID(),
      'x-request-id': config.generateUUID(),
      'x-transaction-id': config.generateUUID()
    };
    
    // Apply overrides
    for (var key in overrides) {
      if (overrides[key] === null) {
        delete headers[key];
      } else {
        headers[key] = overrides[key];
      }
    }
    
    return headers;
  };
  
  // Environment specific configuration
  if (env === 'dev') {
    config.baseUrl = 'http://localhost:8080';
  }
  else if (env === 'qa') {
    config.baseUrl = 'http://qa-api.example.com:8080';
  }
  else if (env === 'prod') {
    config.baseUrl = 'http://api.example.com:8080';
  }
  
  karate.configure('connectTimeout', config.timeout);
  karate.configure('readTimeout', config.timeout);
  karate.configure('retry', { count: config.retry, interval: 5000 });
  
  return config;
}