/** @type {import('next').NextConfig} */
const nextConfig = {
  // 强制去除尾部斜杠 (比如 /guide/dyson-v8/ 会跳到 /guide/dyson-v8)
  trailingSlash: false, 
};

export default nextConfig;
