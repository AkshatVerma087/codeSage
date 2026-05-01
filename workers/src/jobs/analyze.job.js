const { processAnalysis } = require('../processors/analysis.processor');
const Job = require('../models/job.model');
const logger = require('../utils/logger');

async function process(job) {
    const dbJobId = job.data?.jobId ?? null;
    const meta = {
        queueJobId: job.id,
        dbJobId,
        correlationId: job.data?.correlationId ?? null,
        repoId: job.data?.repoId ?? null,
    };

    try {
        if (dbJobId) {
            await Job.findByIdAndUpdate(dbJobId, { status: 'running', startedAt: new Date() });
        }

        logger.info('processing started', meta);

        const result = await processAnalysis(job.data);

        if (dbJobId) {
            await Job.findByIdAndUpdate(dbJobId, { status: 'success', completedAt: new Date() });
        }

        logger.info('processing finished', { ...meta, result });
        return result;
    } catch (err) {
        if (dbJobId) {
            await Job.findByIdAndUpdate(dbJobId, {
                status: 'failed',
                completedAt: new Date(),
                errorMessage: err.message,
            });
        }

        logger.error('processing failed', { ...meta, errorMessage: err.message });
        throw err;
    }
}

module.exports = {
    process,
};