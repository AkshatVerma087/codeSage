const mongoose = require('mongoose');

const repoSchema = new mongoose.Schema({
    ownerUserId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
    },
    provider: {
        type: String,
        required: true,
    }, 
    url: {
        type: String,
        required: true,
    },
    defaultBranch: {
        type: String,
        required: true,
    },
    visibilityHint: {
        type: String,
        enum: ['public', 'private', 'internal'],
        required: true,
    },
    credentialRef: {
        type: String,
        required: false,
        default: null,
    },
    createdAt: {
        type: Date,
        default: Date.now,
    },
    updatedAt: {
        type: Date,
        default: Date.now,
    }
}, { timestamps: true });

const Repo = mongoose.model('Repo', repoSchema);

module.exports = Repo;


//  modules/repos/repo.model.js — _id, ownerUserId, provider, url, defaultBranch, visibilityHint, credentialRef, createdAt, updatedAt