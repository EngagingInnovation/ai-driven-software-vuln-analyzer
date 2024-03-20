// Insecure Direct Object Reference (IDOR)
// In this example, a web application uses user-supplied input to fetch sensitive data, without properly verifying that the user has the authority to access that data.
// Assume req.params.userId comes from the URL path, e.g., /user/12345
app.get('/user/:userId', (req, res) => {
    // Insecure: Directly using user input to fetch user details
    const userId = req.params.userId;
    const query = `SELECT * FROM users WHERE id = ${userId}`;
    
    database.query(query, (error, user) => {
        if (error) {
            return res.status(500).send('Error fetching user data');
        }
        res.json(user);
    });
});
