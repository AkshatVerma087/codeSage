const Repo = require('../models/repo.model');

async function createRepo(req, res) {
    try {
        const { provider, url, defaultBranch, visibilityHint, credentialRef } = req.body;

        const ownerUserId = req.user.id;

        if (!provider || !url || !defaultBranch || !visibilityHint) {
            return res.status(400).json({ message: 'Missing required fields' });
        }

        if (!['public', 'private', 'internal'].includes(visibilityHint)) {
            return res.status(400).json({ message: 'Invalid visibility hint' });
        }

        const existingRepo = await Repo.findOne({ ownerUserId, url, provider, defaultBranch });
        if (existingRepo) {
            return res.status(400).json({ message: 'Repository with this URL already exists for the user' });
        }

        const newRepo = new Repo({
            ownerUserId: req.user.id,
            provider,
            url,
            defaultBranch,
            visibilityHint,
            credentialRef: credentialRef || null,
        });

        await newRepo.save();

        return res.status(201).json({
            success: true,
            message: 'Repository created successfully',
            repo: newRepo
        })
    } catch (error) {
        console.error("Error creating repo:", error);
        return res.status(500).json({ message: 'Internal server error' });
    }

}


async function getRepos(req, res){
    try{
        const ownerUserId = req.user.id;

        const repos = await Repo.find({ ownerUserId }).sort({ createdAt: -1 });

        return res.status(200).json({
            success: true,
            message: 'Repositories retrieved successfully',
            repos: repos,
            count: repos.length
        });
    } catch (error) {
        console.error("Error retrieving repos:", error);
        return res.status(500).json({ message: 'Internal server error' });
    }
}

async function getRepoById(req, res){
    try{
        const {repoId} = req.params;
        const ownerUserId = req.user.id;

        if(!repoId.match(/^[0-9a-fA-F]{24}$/)){
            return res.status(400).json({
                success: false,
                message: 'Invalid repository ID format'
             })
        }
        
        const repo = await Repo.findOne({ _id: repoId, ownerUserId });
        if (!repo) {
            return res.status(404).json({
                success: false,
                message: 'Repository not found'
            });
        }

        if(repo.ownerUserId.toString() !== ownerUserId){
            return res.status(403).json({
                success: false,
                message: 'Unauthorized access to this repository'
            });
        }

        return res.status(200).json({
            success: true,
            message: 'Repository retrieved successfully',
            repo: repo
        });
    } catch (error) {
        console.error("Error retrieving repository:", error);
        return res.status(500).json({ message: 'Internal server error' });
    }
}

async function deleteRepo(req, res){
    try{
        const {repoId} = req.params;
        const ownerUserId = req.user.id;

        if(!repoId.match(/^[0-9a-fA-F]{24}$/)){
            return res.status(400).json({
                success: false,
                message: 'Invalid repository ID format'
             })
        }

        const repo = await Repo.findOne({ _id: repoId, ownerUserId });
        if (!repo) {
            return res.status(404).json({
                success: false,
                message: 'Repository not found'
            });
        }

        await Repo.findByIdAndDelete(repoId);

        return res.status(200).json({
            success: true,
            message: 'Repository deleted successfully'
        });
    } catch (error) {
        console.error("Error deleting repository:", error);
        return res.status(500).json({ message: 'Internal server error' });
    }
}

module.exports = { createRepo, getRepos, getRepoById, deleteRepo };