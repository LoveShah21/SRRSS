const express = require('express');
const User = require('../models/User');
const { authenticate, generateToken, revokeToken } = require('../middleware/auth');
const { authorize } = require('../middleware/rbac');
const router = express.Router();

// Candidate Registration
router.post('/register', async (req, res) => {
  try {
    const { name, email, password, role } = req.body;
    if (!name || !email || !password) {
      return res.status(400).json({ error: 'name, email and password are required' });
    }

    if (password.length < 8) {
      return res.status(400).json({ error: 'Password must be at least 8 characters' });
    }

    const requestedRole = ['Candidate', 'Recruiter'].includes(role) ? role : 'Candidate';
    
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: 'Email already in use' });
    }

    const user = new User({
      name,
      email,
      passwordHash: password,
      role: requestedRole,
      authProvider: 'email',
    });
    await user.save();

    const token = generateToken(user);
    res.status(201).json({ token, user: { id: user._id, name: user.name, role: user.role } });
  } catch (err) {
    console.error("Register Error:", err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Candidate Registration via LinkedIn (MVP: mocked identity data)
router.post('/register-linkedin', async (req, res) => {
  try {
    const { name, email, linkedinUrl } = req.body;
    if (!name || !email || !linkedinUrl) {
      return res.status(400).json({ error: 'name, email and linkedinUrl are required' });
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: 'Email already in use' });
    }

    const generatedPassword = `${Date.now()}_linkedin_user`;
    const user = new User({
      name,
      email,
      linkedinUrl,
      passwordHash: generatedPassword,
      role: 'Candidate',
      authProvider: 'linkedin',
    });

    await user.save();
    const token = generateToken(user);
    res.status(201).json({ token, user: { id: user._id, name: user.name, role: user.role } });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/me', authenticate, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-passwordHash');
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.post('/refresh', authenticate, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    if (!user) return res.status(404).json({ error: 'User not found' });
    const token = generateToken(user);
    res.json({ token });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.post('/logout', authenticate, async (req, res) => {
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(' ')[1];
  revokeToken(token);
  res.json({ message: 'Logged out successfully' });
});

router.post('/admin/create-user', authenticate, authorize('Admin'), async (req, res) => {
  try {
    const { name, email, password, role } = req.body;
    if (!name || !email || !password || !role) {
      return res.status(400).json({ error: 'name, email, password and role are required' });
    }

    if (!['Candidate', 'Recruiter', 'Admin'].includes(role)) {
      return res.status(400).json({ error: 'Invalid role' });
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: 'Email already in use' });
    }

    const user = new User({
      name,
      email,
      passwordHash: password,
      role,
      authProvider: 'email',
    });

    await user.save();
    res.status(201).json({ id: user._id, name: user.name, email: user.email, role: user.role });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

// Generic Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: 'email and password are required' });
    }
    
    const user = await User.findOne({ email });
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });

    const isMatch = await user.comparePassword(password);
    if (!isMatch) return res.status(401).json({ error: 'Invalid credentials' });

    const token = generateToken(user);
    res.json({ token, user: { id: user._id, name: user.name, role: user.role } });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
