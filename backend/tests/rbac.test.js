const { authorize } = require('../src/middleware/rbac');

describe('RBAC middleware', () => {
  it('allows access when role is permitted', () => {
    const middleware = authorize('Admin', 'Recruiter');
    const req = { user: { role: 'Recruiter' } };
    const res = { status: jest.fn().mockReturnThis(), json: jest.fn() };
    const next = jest.fn();

    middleware(req, res, next);

    expect(next).toHaveBeenCalled();
    expect(res.status).not.toHaveBeenCalled();
  });

  it('denies access when role is not permitted', () => {
    const middleware = authorize('Admin');
    const req = { user: { role: 'Candidate' } };
    const res = { status: jest.fn().mockReturnThis(), json: jest.fn() };
    const next = jest.fn();

    middleware(req, res, next);

    expect(next).not.toHaveBeenCalled();
    expect(res.status).toHaveBeenCalledWith(403);
  });
});
