// Event Injection: Injecting user input into event handlers or subscriptions in Node.js.
const EventEmitter = require('events');
const emitter = new EventEmitter();
const userInput = 'user_input'; // This should be sanitized
emitter.on(userInput, () => {
  console.log('Event triggered');
});
