const mongoose = require('mongoose');

const applicationSchema = new mongoose.Schema({
  jobId: { type: mongoose.Schema.Types.ObjectId, ref: 'Job', required: true },
  candidateId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  resumeUrl: { type: String, required: true }, // S3 path or local path if development
  status: { 
    type: String, 
    enum: ['Applied', 'Shortlisted', 'Interview', 'Hired', 'Rejected'], 
    default: 'Applied' 
  },
  aiMatchScore: { type: Number },
  aiExtractedData: {
    name: { type: String },
    email: { type: String },
    skills: [{ type: String }],
    education: [{ type: String }],
    experience: [{ type: String }]
  },
  interviewSchedule: {
    scheduledAt: { type: Date },
    mode: { type: String, enum: ['Online', 'Onsite'], default: 'Online' },
    notes: { type: String, default: '' },
  }
}, { timestamps: true });

applicationSchema.index({ jobId: 1, aiMatchScore: -1 });
applicationSchema.index({ candidateId: 1, createdAt: -1 });
applicationSchema.index({ status: 1 });

module.exports = mongoose.model('Application', applicationSchema);
