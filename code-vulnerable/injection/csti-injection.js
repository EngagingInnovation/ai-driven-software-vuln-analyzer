// Client-Side Template Injection (CSTI) occurs when user input is dynamically embedded into web templates and then rendered on the client side
const template = Handlebars.compile(document.getElementById ('template').innerHTML);
const data = JSON.parse(document.getElementById ('user-data').innerHTL);
const output = document.getElementById('output');
output.innerHTML = template(data);
