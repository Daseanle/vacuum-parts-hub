const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Next.js 应用的路径
  dir: './',
})

// Jest 自定义配置
const customJestConfig = {
  // 测试环境设置
  testEnvironment: 'jest-environment-jsdom',

  // 模块路径映射
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },

  // 测试覆盖率配置
  collectCoverageFrom: [
    'app/**/*.{js,jsx,ts,tsx}',
    'components/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/.next/**',
  ],

  // 覆盖率阈值
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 60,
      lines: 60,
      statements: 60,
    },
  },

  // 测试匹配模式
  testMatch: [
    '**/__tests__/**/*.test.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],

  // 忽略的文件
  testPathIgnorePatterns: [
    '/node_modules/',
    '/.next/',
  ],

  // 设置文件
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
}

// 导出配置
module.exports = createJestConfig(customJestConfig)
