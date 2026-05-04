const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
    ownerUserId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
    },
    repoId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Repo',
        required: true,
    },
    type: {
        type: String,
        enum: ['build', 'test', 'deploy'],
        required: true,
    },
    status: {
        type: String,
        enum: ['pending', 'running', 'success', 'failed'],
        default: 'pending',
    },
    attempts: {
        type: Number,
        default: 0,
    },
    queueJobId: {
        type: String,
        required: false,
        default: null,
    },
    startedAt: {
        type: Date,
        default: null,
    },
    completedAt: {
        type: Date,
        default: null,
    },
    errorCode: {
        type: String,
        required: false,
        default: null,
    },
    errorMessage: {
        type: String,
        required: false,
        default: null,
    },
    correlationId: {
        type: String,
        required: false,
        default: null,
    },
    idempotencyKey: {
        type: String,
        required: false,
        unique: true,
        sparse: true,
    },
}, {timestamps: true});

module.exports = mongoose.model('Job', jobSchema);