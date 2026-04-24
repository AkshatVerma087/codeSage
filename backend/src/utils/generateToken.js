const jwt = require('jsonwebtoken');

const generateToken = (user) => {
    return jwt.sign({ id: user }, process.env.JWT_SECRET, { expiresIn: '1d' });
}

module.exports = generateToken;