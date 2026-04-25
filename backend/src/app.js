const express = require('express');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));


const authRoutes = require('./routes/auth.route');
const repoRoutes = require('./routes/repo.route');



app.use(cookieParser());




app.get('/health', ( req, res) => {
	res.status(200).json({
		status: 'ok',
		service: 'backend',
		timestamp: new Date().toISOString(),
	});
});





app.use('/api/auth', authRoutes);
app.use('/api/repos', repoRoutes);


module.exports = app;
