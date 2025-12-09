import { getAllModelSlugs } from '@/lib/vacuum-data';
import ModelList from '@/components/ModelList';

export default async function Home() {
  // 1. 在服务端获取所有数据
  const guides = await getAllModelSlugs();

  return (
    <main className="flex min-h-screen flex-col items-center py-24 px-4 bg-gray-50">
      {/* 头部区域 */}
      <div className="text-center mb-12 max-w-2xl">
        <h1 className="text-5xl md:text-6xl font-extrabold text-blue-600 mb-6 tracking-tight">
          VacuumPartsHub
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 leading-relaxed">
          Don't throw it away. <span className="font-bold text-gray-800">Fix it.</span>
          <br />
          Free AI-powered repair guides & parts locator.
        </p>
      </div>
      
      {/* 2. 把数据传给客户端组件，进行渲染和交互 */}
      <ModelList models={guides} />
      
      {/* 底部 SEO 文本 */}
      <div className="mt-20 text-center text-sm text-gray-400 max-w-lg">
        <p>Supported Brands: Dyson, Shark, Bissell, iRobot, Black+Decker & more.</p>
        <p className="mt-2">© 2025 VacuumPartsHub. All rights reserved.</p>
      </div>
    </main>
  );
}
