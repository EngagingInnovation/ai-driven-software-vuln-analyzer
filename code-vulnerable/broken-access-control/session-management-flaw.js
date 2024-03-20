// Session Management Flaws
// This example demonstrates a scenario where a user's session is not properly managed, allowing an attacker to hijack or reuse sessions
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const user = authenticate(username, password);
    
    if (user) {
        // Insecure: Session identifier not regenerated after login
        req.session.userId = user.id;
        res.redirect('/dashboard');
    } else {
        res.status(401).send('Login failed');
    }
});
