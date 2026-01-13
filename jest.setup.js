// Jest 测试环境设置
import '@testing-library/jest-dom'

// 模拟 Next.js 路由
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    }
  },
  usePathname() {
    return ''
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

// 模拟环境变量
process.env.NEXT_PUBLIC_SITE_URL = 'http://localhost:3000'

// 全局测试超时
jest.setTimeout(10000)
