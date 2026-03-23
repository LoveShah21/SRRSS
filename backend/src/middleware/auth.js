const jwt = require('jsonwebtoken');
const tokenBlacklist = new Set();

const authenticate = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Authentication required. Token missing.' });
    }

    const token = authHeader.split(' ')[1];
    if (tokenBlacklist.has(token)) {
      return res.status(401).json({ error: 'Token revoked. Please login again.' });
    }
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Attach user record to request
    req.user = decoded;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired.' });
    }
    return res.status(401).json({ error: 'Invalid token.' });
  }
};

const generateToken = (user) => {
  return jwt.sign(
    { id: user._id, role: user.role, email: user.email }, 
    process.env.JWT_SECRET, 
    { expiresIn: process.env.JWT_EXPIRES_IN }
  );
};

const revokeToken = (token) => {
  if (token) tokenBlacklist.add(token);
};

module.exports = { authenticate, generateToken, revokeToken };
