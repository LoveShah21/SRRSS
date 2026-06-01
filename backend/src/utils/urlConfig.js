function normalizeClientOrigin(origin) {
  return String(origin || '')
    .trim()
    .replace(/^['"]+|['"]+$/g, '')
    .replace(/\/+$/, '');
}

function getAllowedClientOrigins() {
  const rawOrigins = [process.env.CLIENT_URL, process.env.FRONTEND_URL]
    .filter(Boolean)
    .flatMap((value) => String(value).split(','));

  const origins = rawOrigins
    .map((origin) => normalizeClientOrigin(origin))
    .filter(Boolean);

  if (origins.length > 0) {
    return Array.from(new Set(origins));
  }

  return ['http://localhost:5173'];
}

function getPrimaryClientUrl() {
  return getAllowedClientOrigins()[0] || 'http://localhost:5173';
}

module.exports = {
  getAllowedClientOrigins,
  getPrimaryClientUrl,
  normalizeClientOrigin,
};
