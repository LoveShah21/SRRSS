const express = require('express');
const Job = require('../models/Job');
const Application = require('../models/Application');
const AuditLog = require('../models/AuditLog');
const { authenticate } = require('../middleware/auth');
const { authorize } = require('../middleware/rbac');
const aiService = require('../services/aiService');
const router = express.Router();

// GET all active jobs (Public / Candidates inside portal)
router.get('/', async (req, res) => {
  try {
    const { status = 'Open', q = '' } = req.query;
    const filter = { status };
    if (q) {
      filter.$text = { $search: q };
    }
    const jobs = await Job.find(filter).sort({ createdAt: -1 });
    res.json(jobs);
  } catch (err) {
    res.status(500).json({ error: 'Server error fetching jobs' });
  }
});

// POST to create a new job (Recruiter / Admin only)
router.post('/', authenticate, authorize('Recruiter', 'Admin'), async (req, res) => {
  try {
    const { title, description, department } = req.body;
    if (!title || !description || !department) {
      return res.status(400).json({ error: 'title, description and department are required' });
    }
    const biasResult = description ? await aiService.detectBias(description) : { biased_words_found: [] };
    const job = new Job({
      ...req.body,
      createdBy: req.user.id,
      biasFlags: biasResult.biased_words_found || [],
    });
    await job.save();
    await AuditLog.create({
      action: 'JOB_CREATED',
      actorId: req.user.id,
      entityType: 'Job',
      entityId: job._id,
      metadata: { title: job.title, department: job.department },
    });
    res.status(201).json(job);
  } catch (err) {
    res.status(500).json({ error: 'Server error creating job' });
  }
});

router.get('/mine', authenticate, authorize('Recruiter', 'Admin'), async (req, res) => {
  try {
    const filter = req.user.role === 'Admin' ? {} : { createdBy: req.user.id };
    const jobs = await Job.find(filter).sort({ createdAt: -1 });
    res.json(jobs);
  } catch (err) {
    res.status(500).json({ error: 'Server error fetching recruiter jobs' });
  }
});

// GET specific job with candidates (Recruiter / Admin only)
router.get('/:id/candidates', authenticate, authorize('Recruiter', 'Admin'), async (req, res) => {
  try {
    const { skills, minYears } = req.query;

    const job = await Job.findById(req.params.id);
    if (!job) return res.status(404).json({ error: 'Job not found' });
    if (req.user.role === 'Recruiter' && String(job.createdBy) !== String(req.user.id)) {
      return res.status(403).json({ error: 'Forbidden for this job' });
    }

    const applications = await Application.find({ jobId: req.params.id })
      .populate('candidateId', 'name email profile')
      .sort({ aiMatchScore: -1 });

    const requiredSkills = (skills || '')
      .split(',')
      .map((skill) => skill.trim().toLowerCase())
      .filter(Boolean);

    const minExperienceYears = Number(minYears || 0);

    const filtered = applications.filter((application) => {
      const profile = application.candidateId?.profile || {};
      const candidateSkills = (profile.skills || []).map((skill) => String(skill).toLowerCase());
      const skillPass =
        requiredSkills.length === 0 || requiredSkills.every((skill) => candidateSkills.includes(skill));

      const experienceYears = (profile.experience || []).reduce((sum, entry) => {
        const duration = String(entry.duration || '0').toLowerCase();
        const yearMatch = duration.match(/(\d+(?:\.\d+)?)\s*year/);
        return sum + (yearMatch ? Number(yearMatch[1]) : 0);
      }, 0);

      const experiencePass = experienceYears >= minExperienceYears;
      return skillPass && experiencePass;
    });

    res.json(filtered);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/analytics/summary', authenticate, authorize('Admin', 'Recruiter'), async (req, res) => {
  try {
    const jobFilter = req.user.role === 'Admin' ? {} : { createdBy: req.user.id };
    const jobs = await Job.find(jobFilter).select('_id');
    const jobIds = jobs.map((j) => j._id);

    const totalJobs = jobIds.length;
    const totalApplications = await Application.countDocuments({ jobId: { $in: jobIds } });
    const hiredCount = await Application.countDocuments({ jobId: { $in: jobIds }, status: 'Hired' });
    const interviewedCount = await Application.countDocuments({ jobId: { $in: jobIds }, status: 'Interview' });

    res.json({
      totalJobs,
      totalApplications,
      hiredCount,
      interviewedCount,
      timeToHireNote: 'Track createdAt to Hired transition in future iteration',
    });
  } catch (err) {
    res.status(500).json({ error: 'Server error fetching analytics summary' });
  }
});

module.exports = router;
