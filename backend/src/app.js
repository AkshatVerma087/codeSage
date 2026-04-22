const express = require('express');

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/health', (_req, res) => {
	res.status(200).json({
		status: 'ok',
		service: 'backend',
		timestamp: new Date().toISOString(),
	});
});

module.exports = app;
