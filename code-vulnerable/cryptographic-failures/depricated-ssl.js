// SSLv2 or SSLv3 for secure communication: These versions of SSL are deprecated and vulnerable.
const https = require('https');
const options = {
  secureProtocol: 'SSLv3_method'
};
