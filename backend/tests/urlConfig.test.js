const { getAllowedClientOrigins, getPrimaryClientUrl, normalizeClientOrigin } = require('../src/utils/urlConfig');

describe('urlConfig', () => {
  const originalClientUrl = process.env.CLIENT_URL;
  const originalFrontendUrl = process.env.FRONTEND_URL;

  afterEach(() => {
    if (originalClientUrl === undefined) delete process.env.CLIENT_URL;
    else process.env.CLIENT_URL = originalClientUrl;

    if (originalFrontendUrl === undefined) delete process.env.FRONTEND_URL;
    else process.env.FRONTEND_URL = originalFrontendUrl;

    jest.resetModules();
  });

  it('normalizes quoted origins and trailing slashes', () => {
    expect(normalizeClientOrigin('"https://srrss.codes/"')).toBe('https://srrss.codes');
  });

  it('merges CLIENT_URL and FRONTEND_URL values', () => {
    process.env.CLIENT_URL = 'https://srrss.codes,https://www.srrss.codes';
    process.env.FRONTEND_URL = '"https://srrss-z5yz.onrender.com"';

    expect(getAllowedClientOrigins()).toEqual([
      'https://srrss.codes',
      'https://www.srrss.codes',
      'https://srrss-z5yz.onrender.com',
    ]);
  });

  it('returns the first normalized client origin as the primary URL', () => {
    process.env.CLIENT_URL = '"https://srrss.codes/"';
    process.env.FRONTEND_URL = 'https://www.srrss.codes';

    expect(getPrimaryClientUrl()).toBe('https://srrss.codes');
  });
});
