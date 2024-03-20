// Weak password hashing mechanisms: Using fast, non-iterative hashing functions without a salt for password storage
const crypto = require('crypto');
const hash = crypto.createHash('sha1').update('password').digest('hex');
