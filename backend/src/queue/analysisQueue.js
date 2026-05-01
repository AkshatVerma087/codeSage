const { Queue } = require('bullmq');
const connection = require('./connection');

const analysisQueue = new Queue('analysis', { connection });

module.exports = analysisQueue;