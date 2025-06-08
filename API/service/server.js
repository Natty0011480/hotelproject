// server.js
const express = require('express');
const app = express();
const notifyHandler = require('./notify');

// Middleware
app.use('/', notifyHandler);

// Start server (e.g., port 3000)
app.listen(3000, () => {
    console.log('Server listening on port 3000');
});
