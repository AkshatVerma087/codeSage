const logger = require('../utils/logger');
const aiClient = require('../services/aiClient');
const util = require('util');

async function processAnalysis(jobData) {
  logger.info('process started', {
    jobId: jobData.jobId,
    correlationId: jobData.correlationId,
    repoId: jobData.repoId,
  });

  const stream = await aiClient.analyze(jobData);

  return new Promise((resolve, reject) => {
    let transcript = '';

    stream.on('data', (chunk) => {
      const text = chunk.toString('utf8');
      transcript += text;

      logger.info('ai stream chunk', {
        jobId: jobData.jobId,
        correlationId: jobData.correlationId,
        chunk: text.trim(),
      });
    });

    stream.on('end', () => {
      logger.info('process completed', {
        jobId: jobData.jobId,
        correlationId: jobData.correlationId,
      });

      resolve({ status: 'success', transcript });
    });

    stream.on('error', (err) => {
      logger.error('ai stream failed', {
        jobId: jobData.jobId,
        correlationId: jobData.correlationId,
        errorMessage: err && err.message ? err.message : String(err),
        errorStack: err && err.stack ? err.stack : null,
        errorObject: util.inspect(err, { depth: 2 }),
      });

      reject(err);
    });
  });
}

module.exports = {
  processAnalysis,
};