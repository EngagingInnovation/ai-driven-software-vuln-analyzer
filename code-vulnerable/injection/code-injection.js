// Code Injection: Evaluating code that includes user input can lead to code injection.
const userInput = 'user_input'; // This should be sanitized
eval(userInput);
