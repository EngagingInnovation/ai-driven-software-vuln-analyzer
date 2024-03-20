// NoSQL Injection: Using user-controlled input directly in NoSQL queries without proper sanitization or parameterization.
const MongoClient = require('mongodb').MongoClient;
const userInput = 'user_input'; // This should be sanitized
MongoClient.connect('mongodb://localhost:27017/', (err, client) => {
  const db = client.db('database');
  const collection = db.collection('users');
  collection.find({ username: userInput }).toArray((err, docs) => {
    // process documents
  });
});
