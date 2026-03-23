const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    index: true,
  },
  passwordHash: {
    type: String,
    required: true,
  },
  role: {
    type: String,
    enum: ['Candidate', 'Recruiter', 'Admin'],
    default: 'Candidate',
  },
  authProvider: {
    type: String,
    enum: ['email', 'linkedin'],
    default: 'email',
  },
  linkedinUrl: {
    type: String,
    default: '',
  },
  // Simple embedded profile structure for Candidates
  profile: {
    summary: { type: String, default: '' },
    skills: [String],
    education: [{ institution: String, degree: String, year: String }],
    experience: [{ company: String, title: String, duration: String }]
  }
}, { timestamps: true });

userSchema.index({ role: 1, createdAt: -1 });

// Hash password before saving
userSchema.pre('save', async function(next) {
  if (!this.isModified('passwordHash')) return next();
  try {
    const salt = await bcrypt.genSalt(10);
    this.passwordHash = await bcrypt.hash(this.passwordHash, salt);
    next();
  } catch (err) {
    next(err);
  }
});

// Method to verify password
userSchema.methods.comparePassword = async function(candidatePassword) {
  return await bcrypt.compare(candidatePassword, this.passwordHash);
};

module.exports = mongoose.model('User', userSchema);
