const express = require('express');
const {register, login, logout} = require('../controllers/auth.controller');
const {authMiddleware, validateLogin, validateRegister} = require('../middlewares/auth.middleware');

const router = express.Router();



router.post('/register', validateRegister, register);
router.post('/login', validateLogin, login);
router.post('/logout', authMiddleware, logout);


module.exports = router;