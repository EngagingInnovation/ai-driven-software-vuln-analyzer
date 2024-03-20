// Server-Side Template Injection: Passing user input directly into templates can lead to server-side template injection.
const ejs = require('ejs');
const userInput = 'user_input'; // This should be sanitized
ejs.render('<%= userInput %>', { userInput }, (err, str) => {
  // process str
});
