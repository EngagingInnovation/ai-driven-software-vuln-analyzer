// SQL Injection: Using concatenation to build SQL queries can lead to SQL injection vulnerabilities.
const mysql = require('mysql');
const connection = mysql.createConnection({ /* connection details */ });
const userInput = 'user_input'; // This should be sanitized
const query = "SELECT * FROM users WHERE username = '" + userInput + "'";
connection.query(query, (error, results) => {
  // process results
});
