const request = require('supertest');
const { app } = require('../src/index');

describe('Health API', () => {
  it('returns OK status', async () => {
    const response = await request(app).get('/api/health');
    expect(response.status).toBe(200);
    expect(response.body.status).toBe('OK');
  });
});
