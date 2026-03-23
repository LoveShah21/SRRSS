const express = require('express')
const { authenticate } = require('../middleware/auth')
const { authorize } = require('../middleware/rbac')
const User = require('../models/User')
const Job = require('../models/Job')
const Application = require('../models/Application')

const router = express.Router()

router.use(authenticate, authorize('Admin'))

router.get('/users', async (req, res) => {
  try {
    const users = await User.find({}, 'name email role createdAt').sort({ createdAt: -1 })
    res.json(users)
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users' })
  }
})

router.patch('/users/:id/role', async (req, res) => {
  try {
    const { role } = req.body
    if (!['Admin', 'Recruiter', 'Candidate'].includes(role)) {
      return res.status(400).json({ error: 'Invalid role' })
    }

    const user = await User.findByIdAndUpdate(req.params.id, { role }, { new: true })
    if (!user) {
      return res.status(404).json({ error: 'User not found' })
    }

    res.json({ id: user._id, name: user.name, email: user.email, role: user.role })
  } catch (error) {
    res.status(500).json({ error: 'Failed to update user role' })
  }
})

router.get('/analytics', async (req, res) => {
  try {
    const [users, jobs, applications, hiredApplications] = await Promise.all([
      User.countDocuments(),
      Job.countDocuments(),
      Application.countDocuments(),
      Application.find({ status: 'Hired' }).populate('jobId', 'createdAt'),
    ])

    let totalDays = 0
    let count = 0
    for (const record of hiredApplications) {
      if (record.jobId?.createdAt) {
        const days = (new Date(record.updatedAt) - new Date(record.jobId.createdAt)) / (1000 * 60 * 60 * 24)
        if (days >= 0) {
          totalDays += days
          count += 1
        }
      }
    }

    const timeToHireDays = count === 0 ? 0 : Number((totalDays / count).toFixed(1))

    const sourceQuality = {
      direct: 0,
      linkedin: 0,
      referral: 0,
    }

    res.json({
      totals: { users, jobs, applications },
      metrics: { timeToHireDays, sourceQuality },
    })
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch analytics' })
  }
})

module.exports = router
