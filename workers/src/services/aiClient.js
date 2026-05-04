const axios = require('axios');

async function analyze(jobData) {
    if (!process.env.AI_SERVICE_URL) {
        throw new Error('AI_SERVICE_URL is not configured in worker environment');
    }

    const baseUrl = process.env.AI_SERVICE_URL.replace(/\/$/, '');
    const response = await axios.post(
        `${baseUrl}/analyze`,
        jobData,
        {
            responseType: 'stream',
            timeout: 0
        }
    );
    return response.data;
}

module.exports = {
    analyze
};