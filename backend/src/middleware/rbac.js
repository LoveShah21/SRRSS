/**
 * Role-Based Access Control Middleware
 * @param {...String} allowedRoles - e.g., 'Admin', 'Recruiter'
 */
const authorize = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user || !req.user.role) {
      return res.status(403).json({ error: 'Missing user role. Ensure authentication precedes authorization.' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Forbidden: Insufficient privileges.' });
    }

    next();
  };
};

module.exports = { authorize };
