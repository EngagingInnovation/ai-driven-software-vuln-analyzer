// Server-Side JavaScript Injection: Similar to code injection, injecting user input into server-side JavaScript execution contexts.
const vm = require('vm');
const userInput = 'user_input'; // This should be sanitized
vm.runInNewContext(userInput);
