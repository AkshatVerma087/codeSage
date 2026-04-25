const express = require('express');
const router = express.Router();
const RepoController = require('../controllers/repo.controller');
const { authMiddleware } = require('../middlewares/auth.middleware');


router.post('/create', authMiddleware, RepoController.createRepo);
router.get('/', authMiddleware, RepoController.getRepos);
router.get('/:repoId', authMiddleware, RepoController.getRepoById);
router.delete('/:repoId', authMiddleware, RepoController.deleteRepo);

module.exports = router;