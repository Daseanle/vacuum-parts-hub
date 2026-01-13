import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Metadata } from 'next';
import vacuums from '@/data/vacuums.json'; // 确保路径对
import { Battery, Wind, Wrench, AlertTriangle, ShoppingCart, ArrowLeft } from 'lucide-react';

// 1. 生成静态路径 (SSG)
export async function generateStaticParams() {
  return vacuums.map((vacuum) => ({
    model: vacuum.slug,
  }));
}

// 2. 动态 SEO Metadata
export async function generateMetadata({ params }: { params: { model: string } }): Promise<Metadata> {
  const vacuum = vacuums.find((v) => v.slug === params.model);
  if (!vacuum) return { title: 'Vacuum Not Found' };

  return {
    title: `Best Parts for ${vacuum.model} (${vacuum.releaseYear}) - Filters, Batteries & Guide`,
    description: `Fix your ${vacuum.brand} ${vacuum.model} easily. Top-rated replacement batteries, ${vacuum.filterType}, and attachments for this ${vacuum.type}. Troubleshooting guide included.`,
    keywords: [`${vacuum.model} parts`, `${vacuum.model} battery`, `${vacuum.model} filter`, "dyson repair"],
  };
}

// 3. 生成亚马逊链接工具
const getAmazonLink = (term: string) => {
  const tag = "vacuumpartshu-20"; // 你的 ID
  return `https://www.amazon.com/s?k=${encodeURIComponent(term)}&tag=${tag}`;
};

export default function DysonModelPage({ params }: { params: { model: string } }) {
  const vacuum = vacuums.find((v) => v.slug === params.model);

  if (!vacuum) {
    return notFound();
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <div className="max-w-3xl mx-auto px-4 py-12">
        
        {/* 顶部导航 */}
        <Link href="/" className="inline-flex items-center text-sm text-gray-500 hover:text-blue-600 mb-8">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Home
        </Link>

        {/* 标题区 */}
        <header className="mb-10">
          <div className="inline-block bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded mb-2">
            {vacuum.releaseYear} Model
          </div>
          <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
            Maintain Your {vacuum.brand} {vacuum.model}
          </h1>
          <p className="text-xl text-gray-600">
            Essential parts guide and troubleshooting for the {vacuum.type}.
          </p>
        </header>

        {/* 参数规格卡片 (增加页面独特性) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center">
            <div className="bg-green-100 p-2 rounded-lg mr-3">
              <Battery className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase font-bold">Runtime</p>
              <p className="font-semibold text-gray-800">{vacuum.batteryLife}</p>
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center">
            <div className="bg-purple-100 p-2 rounded-lg mr-3">
              <Wind className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase font-bold">Filter Type</p>
              <p className="font-semibold text-gray-800">{vacuum.filterType}</p>
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center">
            <div className="bg-orange-100 p-2 rounded-lg mr-3">
              <Wrench className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase font-bold">Key Feature</p>
              <p className="font-semibold text-gray-800">{vacuum.features[0]}</p>
            </div>
          </div>
        </div>

        {/* 核心购买区 (Lucide 图标替代产品图，防侵权) */}
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Essential Replacement Parts</h2>
        <div className="grid gap-4">
          
          {/* 电池卡片 */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex justify-between items-center">
            <div className="flex items-center">
              <div className="bg-gray-100 p-3 rounded-full mr-4">
                <Battery className="w-8 h-8 text-gray-600" />
              </div>
              <div>
                <h3 className="font-bold text-lg text-gray-900">Replacement Battery</h3>
                <p className="text-sm text-gray-500">Fix runtime issues. Recommended every 2-3 years.</p>
              </div>
            </div>
            <a 
              href={getAmazonLink(`${vacuum.brand} ${vacuum.model} replacement battery`)}
              target="_blank"
              rel="nofollow noreferrer"
              className="bg-yellow-400 hover:bg-yellow-500 text-black font-bold py-2 px-6 rounded-lg shadow-sm transition-colors flex items-center"
            >
              Check Price <ShoppingCart className="w-4 h-4 ml-2" />
            </a>
          </div>

          {/* 滤芯卡片 */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex justify-between items-center">
            <div className="flex items-center">
              <div className="bg-gray-100 p-3 rounded-full mr-4">
                <Wind className="w-8 h-8 text-gray-600" />
              </div>
              <div>
                <h3 className="font-bold text-lg text-gray-900">HEPA Filter Kit</h3>
                <p className="text-sm text-gray-500">Fix pulsing issues and improve suction.</p>
              </div>
            </div>
            <a 
              href={getAmazonLink(`${vacuum.brand} ${vacuum.model} filter replacement`)}
              target="_blank"
              rel="nofollow noreferrer"
              className="bg-yellow-400 hover:bg-yellow-500 text-black font-bold py-2 px-6 rounded-lg shadow-sm transition-colors flex items-center"
            >
              Check Price <ShoppingCart className="w-4 h-4 ml-2" />
            </a>
          </div>

          {/* 配件卡片 */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex justify-between items-center">
            <div className="flex items-center">
              <div className="bg-gray-100 p-3 rounded-full mr-4">
                <Wrench className="w-8 h-8 text-gray-600" />
              </div>
              <div>
                <h3 className="font-bold text-lg text-gray-900">Attachments & Tools</h3>
                <p className="text-sm text-gray-500">Crevice tools, soft rollers, and more.</p>
              </div>
            </div>
            <a 
              href={getAmazonLink(`${vacuum.brand} ${vacuum.model} attachments`)}
              target="_blank"
              rel="nofollow noreferrer"
              className="bg-yellow-400 hover:bg-yellow-500 text-black font-bold py-2 px-6 rounded-lg shadow-sm transition-colors flex items-center"
            >
              Check Price <ShoppingCart className="w-4 h-4 ml-2" />
            </a>
          </div>

        </div>

        {/* 故障诊断区 (增加 SEO 内容厚度) */}
        <div className="mt-12 bg-blue-50 p-8 rounded-2xl border border-blue-100">
          <h2 className="text-xl font-bold text-blue-900 mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" /> Common {vacuum.model} Issues
          </h2>
          <ul className="list-disc list-inside space-y-2 text-blue-800">
            {vacuum.commonIssues.map((issue, idx) => (
              <li key={idx}>{issue}</li>
            ))}
          </ul>
          <p className="mt-4 text-sm text-blue-700">
            If your <strong>{vacuum.model}</strong> is experiencing these issues, replacing the filters or battery (if it's a {vacuum.type}) is usually the most cost-effective fix compared to buying a new machine.
          </p>
        </div>

        {/* 强制合规页脚 */}
        <footer className="mt-16 pt-8 border-t border-gray-200 text-center text-xs text-gray-400">
          <p className="mb-2">VacuumPartsHub is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com.</p>
          <p>© 2025 VacuumPartsHub. All rights reserved.</p>
        </footer>

      </div>
    </div>
  );
}
