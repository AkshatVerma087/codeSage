const express = require('express');
const router = express.Router();
const jobController = require('../controllers/job.controller');
const {authMiddleware: verifyToken} = require('../middlewares/auth.middleware');


router.post('/analyze', verifyToken, jobController.triggerAnalysis);

module.exports = router;