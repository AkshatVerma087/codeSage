const Job = require('../models/job.model');
const analysisQueue = require('../queue/analysisQueue');

async function triggerAnalysis(req, res) {
    try{
        const ownerUserId = req.user.id;
        const {repoId, idempotencyKey, correlationId} = req.body;
        const resolvedCorrelationId = correlationId || req.correlationId || null;

        if(!repoId) {
            return res.status(400).json({error: 'repoId is required'});
        }

        // idempotency: if idempotencyKey provided and a job exists, return it
        if (idempotencyKey) {
            const existing = await Job.findOne({ idempotencyKey });
            if (existing) {
                return res.status(200).json({
                    success: true,
                    existing: true,
                    jobId: existing._id,
                    queueJobId: existing.queueJobId,
                    status: existing.status,
                    startedAt: existing.startedAt,
                    completedAt: existing.completedAt,
                });
            }
        }

        const jobPayload = {
            ownerUserId,
            repoId,
            type: 'build',
            status: 'pending',
            attempts: 0,
            correlationId: resolvedCorrelationId,
        };

        if (idempotencyKey) {
            jobPayload.idempotencyKey = idempotencyKey;
        }

        const job = await Job.create(jobPayload);

        const queued = await analysisQueue.add(
            'analysis',
            {
                jobId: job._id.toString(),
                ownerUserId,
                repoId,
                correlationId: resolvedCorrelationId,
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
            queueJobId: job.queueJobId,
            status: job.status,
            correlationId: job.correlationId,
            startedAt: job.startedAt,
            completedAt: job.completedAt,
        });
    }catch(error) {
        console.error('Error triggering analysis:', error);
        return res.status(500).json({error: 'Failed to trigger analysis'});
    }
}

async function getJobById(req, res) {
    try {
        const ownerUserId = req.user.id;
        const { jobId } = req.params;

        if (!jobId || !jobId.match(/^[0-9a-fA-F]{24}$/)) {
            return res.status(400).json({
                success: false,
                error: 'Invalid jobId format',
            });
        }

        const job = await Job.findOne({ _id: jobId, ownerUserId });

        if (!job) {
            return res.status(404).json({
                success: false,
                error: 'Job not found',
            });
        }

        return res.status(200).json({
            success: true,
            job: {
                jobId: job._id,
                ownerUserId: job.ownerUserId,
                repoId: job.repoId,
                type: job.type,
                status: job.status,
                attempts: job.attempts,
                queueJobId: job.queueJobId,
                startedAt: job.startedAt,
                completedAt: job.completedAt,
                errorCode: job.errorCode,
                errorMessage: job.errorMessage,
                correlationId: job.correlationId,
                idempotencyKey: job.idempotencyKey,
                createdAt: job.createdAt,
                updatedAt: job.updatedAt,
            },
        });
    } catch (error) {
        console.error('Error retrieving job:', error);
        return res.status(500).json({ error: 'Failed to retrieve job' });
    }
}

module.exports = {
    triggerAnalysis,
    getJobById,
};