module.exports = {
  testEnvironment: 'jsdom',
  testMatch: ['**/src/**/*.test.jsx'],
  transform: {
    '^.+\\.[jt]sx?$': 'babel-jest',
  },
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/src/test/styleMock.js',
  },
  setupFilesAfterEnv: ['<rootDir>/src/test/setupTests.js'],
};
