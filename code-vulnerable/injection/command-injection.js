// Command Injection: Passing user input directly to functions that execute system commands can lead to command injection.
const { exec } = require('child_process');
const userInput = 'user_input'; // This should be sanitized
exec('ls -la ' + userInput, (error, stdout, stderr) => {
  // process output
});
