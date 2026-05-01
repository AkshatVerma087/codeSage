const Job = require('../models/job.model');
const analysisQueue = require('../queue/analysisQueue');

async function triggerAnalysis(req, res) {
    try{
        const ownerUserId = req.user.id;
        const {repoId, idempotencyKey, correlationId} = req.body;

        if(!repoId) {
            return res.status(400).json({error: 'repoId is required'});
        }

        const job = await Job.create({
            ownerUserId,
            repoId,
            type: 'build',
            status: 'pending',
            attempts: 0,
            idempotencyKey: idempotencyKey || null,
            correlationId: correlationId || null,
        });

        const queued = await analysisQueue.add(
            'analysis',
            {
                jobId: job._id.toString(),
                ownerUserId,
                repoId,
                correlationId: job.correlationId,
            },
            {
                removeOnComplete: true,
                removeOnFail: false,
            }
        );

        job.queueJobId = queued.id?.toString() ?? String(queued.id);
        await job.save();

        return res.status(201).json({
            success: true,
            jobId: job._id,
        });
    }catch(error) {
        console.error('Error triggering analysis:', error);
        return res.status(500).json({error: 'Failed to trigger analysis'});
    }
}

module.exports = {
    triggerAnalysis,
};