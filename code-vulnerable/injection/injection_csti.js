// Client-Side Template Injection (CSTI) occurs when user input is dynamically embedded into web templates and then rendered on the client side
app.get('/', (req, res) => {
  const userInput = req.query.userInput; // User-controlled input
  // Render a template with user-controlled input
  // In this case, if userInput contains template code or scripts, it could lead to CSTI
  res.render('index', { userInput });
});
