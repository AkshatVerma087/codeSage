const mongoose = require('mongoose');

const connectDB = async () => {
	const mongoUri = process.env.MONGO_URI;

	if (!mongoUri) {
		console.warn('MONGO_URI is not set. Starting without database connection.');
		return;
	}

	await mongoose.connect(mongoUri, {
		serverSelectionTimeoutMS: 5000,
	});

	console.log('MongoDB connected');
};

module.exports = connectDB;
