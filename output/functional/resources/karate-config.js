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
      'Aplicacion-Id': karate.properties['header.aplicacion.id'] || 'APP-DEFAULT-001',
      'Nombre-Aplicacion': karate.properties['header.nombre.aplicacion'] || 'Aplicacion-Prueba',
      'Nombre-Servicio-Consumidor': karate.properties['header.nombre.servicio.consumidor'] || 'Servicio-Prueba',
      'Ocp-Apim-Subscription-Key': karate.properties['header.ocp.apim.subscription.key'] || 'default-subscription-key-12345',
      'Transaccion-Id': config.generateUUID(),
      'Usuario-Consumidor-Id': karate.properties['header.usuario.consumidor.id'] || 'USR-DEFAULT-001'
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