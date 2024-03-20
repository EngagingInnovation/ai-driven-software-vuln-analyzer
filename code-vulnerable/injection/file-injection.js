// File Injection: Using user input to determine file paths or contents can lead to file system injection.
const fs = require('fs');
const userInput = 'user_input'; // This should be sanitized
fs.readFile(userInput, 'utf8', (err, data) => {
  // process data
});
