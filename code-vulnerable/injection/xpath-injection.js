// XPath Injection: Dynamically building XPath queries with user input can lead to XPath injection.
const libxmljs = require("libxmljs");
const userInput = 'user_input'; // This should be sanitized
const doc = libxmljs.parseXml("<users><user>John Doe</user></users>");
const xpathQuery = "//user[text()='" + userInput + "']";
const nodes = doc.find(xpathQuery);
