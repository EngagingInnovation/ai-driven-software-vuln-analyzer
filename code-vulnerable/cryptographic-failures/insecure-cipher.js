// RC4 for encryption: RC4 is an outdated and insecure stream cipher. 
const crypto = require('crypto');
const cipher = crypto.createCipher('rc4', secretKey);
