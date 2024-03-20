// DES or 3DES for encryption: These are outdated symmetric encryption algorithms with known vulnerabilities
const crypto = require('crypto');
const cipher = crypto.createCipher('des-ede3-cbc', secretKey);
