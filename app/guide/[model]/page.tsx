import { getModelData, getAllModelSlugs } from '@/lib/vacuum-data';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

export async function generateStaticParams() {
  return await getAllModelSlugs();
}

export async function generateMetadata({ params }: { params: { model: string } }): Promise<Metadata> {
  const data = await getModelData(params.model);
  if (!data) return { title: 'Guide Not Found' };
  return {
    title: `${data.brand} ${data.model} Repair Guide & Parts`,
    description: `Troubleshoot and fix your ${data.brand} ${data.model}. Find manual, common problems, and replacement parts.`,
  };
}

export default async function ModelPage({ params }: { params: { model: string } }) {
  const data = await getModelData(params.model);

  if (!data) {
    return notFound();
  }

  // --- 核心修改：智能图片逻辑 ---
  // 1. 生成一个带文字的占位图链接 (灰色背景，深色文字)
  const placeholderText = `${data.brand} ${data.model}`;
  // 600x400尺寸，背景色蓝色(2563eb)，文字白色(ffffff)
  const placeholderUrl = `https://placehold.co/600x400/2563eb/ffffff?text=${encodeURIComponent(data.brand + '\n' + data.model)}`;
  
  // 2. 优先用 JSON 里的图，如果没有，就用占位图
  // 注意：如果你想强制所有页面都用占位图（为了统一），可以把下面这行改成：const displayImage = placeholderUrl;
  const displayImage = placeholderUrl;

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 font-sans">
      <nav className="text-sm text-gray-500 mb-4">
        <Link href="/" className="hover:text-blue-600">Home</Link> &gt; {data.brand} &gt; {data.model}
      </nav>

      <header className="mb-12 text-center">
        {/* --- 升级版：纯 CSS 生成的维修手册封面 Start --- */}
        <div className="flex justify-center mb-8">
          <div className="relative w-full max-w-lg aspect-video bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl shadow-xl border border-slate-700 flex flex-col items-center justify-center p-8 text-center text-white overflow-hidden group">
            
            {/* 背景装饰（齿轮图标） */}
            <div className="absolute text-white opacity-5 group-hover:opacity-10 transition-opacity duration-500 transform scale-150">
              <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z"/><path d="M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/><path d="M12 2v2"/><path d="M12 22v-2"/><path d="m17 20.66-1-1.73"/><path d="M11 10.27 7 3.34"/><path d="m20.66 17-1.73-1"/><path d="m3.34 7 1.73 1"/><path d="M14 12h8"/><path d="M2 12h2"/><path d="m20.66 7-1.73 1"/><path d="m3.34 17 1.73-1"/><path d="m17 3.34-1 1.73"/><path d="m11 13.73-4 6.93"/></svg>
            </div>

            {/* 品牌名 */}
            <h3 className="text-xl md:text-2xl font-bold text-slate-400 uppercase tracking-widest mb-2 z-10">
              {data.brand}
            </h3>
            
            {/* 型号名 (大字) */}
            <h2 className="text-3xl md:text-4xl font-extrabold text-white leading-tight z-10 drop-shadow-md">
              {data.model}
            </h2>

            {/* 底部标签 */}
            <div className="mt-6 z-10">
              <span className="px-4 py-1.5 bg-blue-600 text-white text-xs font-bold uppercase tracking-wide rounded-full shadow-lg">
                Official Repair Guide
              </span>
            </div>
          </div>
        </div>
        {/* --- 升级版：纯 CSS 生成的维修手册封面 End --- */}

        <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
          {data.brand} {data.model}
          <span className="block text-blue-600 mt-2">Repair Guide</span>
        </h1>
        <p className="text-xl text-gray-600">
          Select your problem below to find the solution.
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        {data.problems.map((problem) => (
          <Link 
            key={problem.id} 
            href={`/guide/${params.model}/${problem.id}`}
            className="block group"
          >
            <div className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow bg-white h-full flex flex-col justify-center">
              <h2 className="text-xl font-bold text-blue-600 group-hover:text-blue-800 mb-2">
                {problem.title}
              </h2>
              <p className="text-gray-600 line-clamp-2 text-sm mb-4">
                {problem.description}
              </p>
              <div className="mt-auto text-sm text-gray-400 font-medium flex items-center">
                View Solution <span className="ml-1 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
