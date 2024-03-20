// Process Injection: Injecting user input into process creation functions.
const { spawn } = require('child_process');
const userInput = 'user_input'; // This should be sanitized
spawn('cmd', [userInput]);
