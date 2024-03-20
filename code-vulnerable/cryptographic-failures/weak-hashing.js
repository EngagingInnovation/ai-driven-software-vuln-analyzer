// MD5 or SHA-1 for hashing: These hashing algorithms are considered weak due to vulnerabilities to collision attacks. 
const crypto = require('crypto');
const hash = crypto.createHash('md5').update('password').digest('hex');
