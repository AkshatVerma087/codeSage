const {queue} = require('bullmq');
const connection = require('./connection');

const analysisQueue = new queue('analysis', {connection});

module.exports = analysisQueue;