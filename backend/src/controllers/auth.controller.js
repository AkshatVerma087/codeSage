const User = require('../models/auth.model');
const bcrypt = require('bcryptjs');
const generateToken = require('../utils/generateToken');
async function register(req, res) {
    const { username, email, password } = req.body;

    try{
        // Check if user already exists
        const existingUser = await User.findOne({ email });
        if(existingUser) {
            return res.status(400).json({ message: 'User already exists' });
        }

        // Create new user
        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({
            username,
            email,
            password: hashedPassword
        });

        await newUser.save();

        const token = generateToken(newUser._id);
        res.cookie('token', token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
            maxAge: 24 * 60 * 60 * 1000 // 1 day
        });
        

        return res.status(201).json({ message: 'User registered successfully', user: { id: newUser._id, username: newUser.username, email: newUser.email }});
    } catch (error) {
        console.error(error);
        return res.status(500).json({ message: 'Internal server error' });
    }

}


async function login(req, res) {
    const { email, password } = req.body;
    try {
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(400).json({ message: 'Invalid credentials' });
        }
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ message: 'Invalid credentials' });
        }
        const token = generateToken(user._id);
        res.cookie('token', token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
            maxAge: 24 * 60 * 60 * 1000 // 1 day
        });
        return res.status(200).json({ message: 'Login successful', user: { id: user._id, username: user.username, email: user.email } });
    } catch (error) {
        console.error(error);
        return res.status(500).json({ message: 'Internal server error' });
    }
}


async function logout(req, res) {
    res.clearCookie('token', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
    });
    return res.status(200).json({ message: 'Logout successful' });
}


module.exports = {
    register,
    login,
    logout
};