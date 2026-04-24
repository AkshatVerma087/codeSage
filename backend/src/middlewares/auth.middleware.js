const jwt = require('jsonwebtoken');
const User = require('../models/auth.model');


async function authMiddleware(req, res, next) {
    let token = req.cookies.token;

    if(!token){
        const authHeader = req.headers.authorization;
        if(authHeader && authHeader.startsWith('Bearer ')){
            token = authHeader.split(' ')[1];
        }
    }

    if(!token) {
        return res.status(401).json({
            message: "Please login to access this resource"
        })
    }

    try{
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.id).select('-password');

        if(!user) {
            return res.status(401).json({
                message: "User not found"
            })
        }

        req.user = user;
        next();
    }catch(err){
        return res.status(401).json({
            message: "Invalid token"
        })
    }
}




function sanitizeString(value) {
    if (typeof value !== 'string') {
        return '';
    }
    return value.trim();
}





function isValidEmail(email) {
     return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}




async function validateRegister(req, res, next) {
    const username = sanitizeString(req.body.username);
    const email = sanitizeString(req.body.email);
    const password = sanitizeString(req.body.password);

    if(!username || !email || !password) {
        return res.status(400).json({
            message: "All fields are required"
        })
    }

    if(!isValidEmail(email)) {
        return res.status(400).json({
            message: "Please provide a valid email"
        })
    }

    if(password.length < 6) {
        return res.status(400).json({
            message: "Password must be at least 6 characters long"
        })
    }

    req.body.username = username;
    req.body.email = email;
    req.body.password = password;

    next();
}


function validateLogin(req, res, next) {
    const email = sanitizeString(req.body.email);
    const password = sanitizeString(req.body.password);

    if(!email || !password) {
        return res.status(400).json({
            message: "All fields are required"
        })
    }

    if(!isValidEmail(email)) {
        return res.status(400).json({
            message: "Please provide a valid email"
        })
    }

    req.body.email = email;
    req.body.password = password;
    return next();
}

module.exports = {
    authMiddleware,
    validateRegister,
    validateLogin
}