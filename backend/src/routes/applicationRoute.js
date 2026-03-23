const express = require('express');
const multer = require('multer');
const Application = require('../models/Application');
const Job = require('../models/Job');
const AuditLog = require('../models/AuditLog');
const { authenticate } = require('../middleware/auth');
const aiService = require('../services/aiService'); // We will create this proxy service next
const router = express.Router();

const upload = multer({ storage: multer.memoryStorage() }); // Read PDF/DOCX to buffer

// POST apply for a job (Candidate only)
router.post('/apply/:jobId', authenticate, upload.single('resume'), async (req, res) => {
  try {
    if (req.user.role !== 'Candidate') return res.status(403).json({ error: 'Only candidates can apply' });
    if (!req.file) return res.status(400).json({ error: 'resume file is required' });

    const jobId = req.params.jobId;
    const job = await Job.findById(jobId);
    if (!job) return res.status(404).json({ error: 'Job not found' });
    if (job.status !== 'Open') return res.status(400).json({ error: 'Job is closed for applications' });

    const alreadyApplied = await Application.findOne({ jobId, candidateId: req.user.id });
    if (alreadyApplied) return res.status(400).json({ error: 'Candidate already applied to this job' });
    
    // 1. Upload file to S3 (stubbed - using dummy URL for now)
    const resumeUrl = `https://dummy-s3-bucket.s3.amazonaws.com/${req.file.originalname}`;

    // 2. Call Python AI Microservice to Parse Resume
    // We send the buffer to FastAPI
    const parsedData = await aiService.parseResume(req.file);

    // 3. Score candidate against the Job Description
    const scoreResult = await aiService.scoreCandidate(job.description, {
      candidateSkills: parsedData?.extracted_data?.skills || [],
      candidateText: parsedData?.raw_text || '',
    });

    // 4. Save to DB
    const application = new Application({
      jobId,
      candidateId: req.user.id,
      resumeUrl,
      aiMatchScore: Number(scoreResult.match_score || 0),
      aiExtractedData: parsedData.extracted_data
    });

    await application.save();
    await AuditLog.create({
      action: 'APPLICATION_CREATED',
      actorId: req.user.id,
      entityType: 'Application',
      entityId: application._id,
      metadata: { jobId, aiMatchScore: application.aiMatchScore },
    });

    res.status(201).json(application);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to process application' });
  }
});

// GET applications for candidate (Candidate view)
router.get('/my-applications', authenticate, async (req, res) => {
  try {
    if (req.user.role !== 'Candidate') {
      return res.status(403).json({ error: 'Only candidates can view personal applications' });
    }
    const apps = await Application.find({ candidateId: req.user.id }).populate('jobId', 'title department');
    res.json(apps);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

// PATCH update application status (Recruiter view)
router.patch('/:id/status', authenticate, async (req, res) => {
    if (req.user.role !== 'Recruiter' && req.user.role !== 'Admin') {
        return res.status(403).json({ error: 'Forbidden' });
    }
    try {
        const allowedStatuses = ['Applied', 'Shortlisted', 'Interview', 'Hired', 'Rejected'];
        if (!allowedStatuses.includes(req.body.status)) {
          return res.status(400).json({ error: 'Invalid status' });
        }

        const app = await Application.findByIdAndUpdate(req.params.id, { status: req.body.status }, { new: true });
        if (!app) return res.status(404).json({ error: 'Application not found' });
        await AuditLog.create({
          action: 'APPLICATION_STATUS_UPDATED',
          actorId: req.user.id,
          entityType: 'Application',
          entityId: app._id,
          metadata: { status: app.status },
        });
        res.json(app);
    } catch (err) {
        res.status(500).json({ error: 'Failed to update status' });
    }
});

// PATCH schedule interview (Recruiter/Admin)
router.patch('/:id/schedule-interview', authenticate, async (req, res) => {
  if (req.user.role !== 'Recruiter' && req.user.role !== 'Admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }

  try {
    const { scheduledAt, mode = 'Online', notes = '' } = req.body;
    if (!scheduledAt) {
      return res.status(400).json({ error: 'scheduledAt is required' });
    }

    const updated = await Application.findByIdAndUpdate(
      req.params.id,
      {
        status: 'Interview',
        interviewSchedule: {
          scheduledAt: new Date(scheduledAt),
          mode,
          notes,
        },
      },
      { new: true }
    );

    if (!updated) return res.status(404).json({ error: 'Application not found' });
    await AuditLog.create({
      action: 'INTERVIEW_SCHEDULED',
      actorId: req.user.id,
      entityType: 'Application',
      entityId: updated._id,
      metadata: { scheduledAt, mode },
    });
    res.json(updated);
  } catch (err) {
    res.status(500).json({ error: 'Failed to schedule interview' });
  }
});

router.get('/job/:jobId', authenticate, async (req, res) => {
  try {
    if (req.user.role !== 'Recruiter' && req.user.role !== 'Admin') {
      return res.status(403).json({ error: 'Forbidden' });
    }
    const applications = await Application.find({ jobId: req.params.jobId })
      .populate('candidateId', 'name email profile')
      .sort({ aiMatchScore: -1 });
    res.json(applications);
  } catch (err) {
    res.status(500).json({ error: 'Failed to get job applications' });
  }
});

router.get('/audit/logs', authenticate, async (req, res) => {
  try {
    if (req.user.role !== 'Admin') {
      return res.status(403).json({ error: 'Only Admin can access audit logs' });
    }
    const logs = await AuditLog.find({}).sort({ createdAt: -1 }).limit(200);
    res.json(logs);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch audit logs' });
  }
});

module.exports = router;
