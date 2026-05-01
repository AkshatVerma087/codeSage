const logger = require('../utils/logger');


async function processAnalysis(jobData) {
    logger.info('process started', {
        jobID: jobData.jobId,
        correlationId: jobData.correlationId,
        repoId: jobData.repoId,
    });


    await new Promise(resolve => setTimeout(resolve, 1000));

    logger.info('process completed', {
        jobID: jobData.jobId,
        correlationId: jobData.correlationId,
    });

    return { status : 'success' };
}

module.exports = {
    processAnalysis,
};