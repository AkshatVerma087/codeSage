const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });
const { Worker } = require('bullmq');
const connection = require('./src/queue/connections');
const analyzeJob = require('./src/jobs/analyze.job');
const logger = require('./src/utils/logger');
const mongoose = require('mongoose');


mongoose.connect(process.env.MONGO_URI)
    .then(() => logger.info('mongo connected'))
    .catch((err) => logger.error('mongo connection failed', { errorMessage: err.message }));

const worker = new Worker(
    'analysis',
    async (job) => {
        const meta = {
            queueJobId: job.id,
            dbJobId: job.data?.jobId ?? null,
            correlationId: job.data?.correlationId ?? null,
            repoId: job.data?.repoId ?? null,
        };

        logger.info('job received', meta);

        const result = await analyzeJob.process(job);

        logger.info('job completed', { ...meta, result });

        return result;
    },
    { connection }
);

const util = require('util');

worker.on('failed', (job, err) => {
    logger.error('job failed', {
        jobId: job?.id ?? null,
        correlationId: job?.data?.correlationId ?? null,
        errorMessage: err && err.message ? err.message : String(err),
        errorStack: err && err.stack ? err.stack : null,
        errorObject: util.inspect(err, { depth: 2 }),
    });
});

worker.on('error', (err) => {
    logger.error('worker error', {
        errorMessage: err.message,
      
    });
});

logger.info('worker started', {queue: 'analysis'});