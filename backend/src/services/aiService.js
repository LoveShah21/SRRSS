const axios = require('axios');
const FormData = require('form-data');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000/api/v1';

const parseResume = async (fileInfo) => {
  try {
    const formData = new FormData();
    formData.append('file', fileInfo.buffer, {
      filename: fileInfo.originalname,
      contentType: fileInfo.mimetype,
    });

    const response = await axios.post(`${AI_SERVICE_URL}/parse-resume`, formData, {
      headers: { ...formData.getHeaders() }
    });

    return response.data;
  } catch (error) {
    console.error("AI Service Error:", error.message);
    // Return a graceful fallback if Python service is down during early dev
    return {
      raw_text: '',
      extracted_data: { skills: [], education: [], experience: [] }
    };
  }
};

const scoreCandidate = async (jobText, candidateData) => {
  try {
    const response = await axios.post(`${AI_SERVICE_URL}/score-candidate`, {
      jobText,
      candidate: candidateData,
      jobSkills: []
    });
    return response.data;
  } catch (error) {
     return { match_score: 0, matched_skills: [] };
  }
};

const detectBias = async (jobDescription) => {
  try {
    const response = await axios.post(`${AI_SERVICE_URL}/detect-bias`, {
      jobDescription,
    });
    return response.data;
  } catch (error) {
    return { biased_words_found: [], recommendation: 'Bias detection service unavailable.' };
  }
};

module.exports = { parseResume, scoreCandidate, detectBias };
