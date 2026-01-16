import { getModelData, getAllModelSlugs } from '@/lib/vacuum-data';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

// 1. 静态路径生成 (保持不变)
export async function generateStaticParams() {
  const models = await getAllModelSlugs();
  return models;
}

// 2. 动态 SEO 元数据 (新增功能：让 Google 标题更性感)
export async function generateMetadata({ params }: { params: { model: string; problem: string } }): Promise<Metadata> {
  const data = await getModelData(params.model);
  const problem = data?.problems.find(p => p.id === params.problem);

  if (!data || !problem) return { title: 'Guide Not Found' };

  return {
    title: `How to Fix: ${problem.title} - ${data.brand} ${data.model}`,
    description: `Step-by-step repair guide for ${data.brand} ${data.model}. Symptoms: ${problem.description}. Find exact replacement parts and fix it yourself.`,
    keywords: [...(data.seo_keywords || []), "repair guide", "troubleshooting", "fix", "replacement parts"],
  };
}

// 3. 亚马逊链接生成器 (确认 ID 是你的)
function getAmazonLink(query: string) {
  const tag = "vacuumpartshu-20"; // <--- 你的真实 ID
  return `https://www.amazon.com/s?k=${encodeURIComponent(query)}&tag=${tag}`;
}

// 4. 页面主组件
export default async function ProblemPage({
  params
}: {
  params: { model: string; problem: string }
}) {
  const data = await getModelData(params.model);

  if (!data) return notFound();

  const problem = data.problems.find(p => p.id === params.problem);
  if (!problem) return notFound();

  // 准备结构化数据 (Schema.org) - 让 Google 搜索结果显示步骤
  const jsonLd: any = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "HowTo",
        "name": `Fix ${data.brand} ${data.model}: ${problem.title}`,
        "description": problem.description,
        "image": data.image_url,
        "step": problem.solution_steps.map((step, index) => ({
          "@type": "HowToStep",
          "position": index + 1,
          "text": step
        })),
        "tool": problem.required_parts.map(part => ({
          "@type": "HowToTool",
          "name": part.name
        }))
      }
    ]
  };

  // Inject FAQ Schema if available
  if (data.faqs && data.faqs.length > 0) {
    jsonLd["@graph"].push({
      "@type": "FAQPage",
      "mainEntity": data.faqs.map(faq => ({
        "@type": "Question",
        "name": faq.question,
        "acceptedAnswer": {
          "@type": "Answer",
          "text": faq.answer
        }
      }))
    });
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 font-sans pb-32">
      {/* 注入结构化数据给爬虫看 */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* 顶部导航 */}
      <Link
        href={`/guide/${params.model}`}
        className="text-blue-600 hover:underline mb-6 inline-block font-medium"
      >
        &larr; Back to {data.model} Overview
      </Link>

      <article className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden p-6 sm:p-8">

        {/* 专家信任标签 (新增) */}
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
          <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded text-xs font-bold tracking-wide uppercase">
            Verified Fix
          </span>
          <span>Based on official {data.brand} service manuals</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-6 leading-tight">
          {problem.title}
        </h1>

        {/* 症状描述框 */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8 rounded-r-lg">
          <p className="font-bold text-yellow-800 text-sm uppercase tracking-wide mb-1">Symptoms</p>
          <p className="text-yellow-900">{problem.description}</p>
        </div>

        {/* 解决方案步骤 */}
        <div className="mb-10">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm mr-3">🛠</span>
            How to Fix It
          </h2>
          <ol className="list-decimal list-outside ml-5 space-y-4">
            {problem.solution_steps.map((step, idx) => (
              <li key={idx} className="text-lg text-gray-700 pl-2 leading-relaxed">
                {step}
              </li>
            ))}
          </ol>
        </div>

        {/* 赚钱模块：配件推荐 (优化了按钮文案) */}
        {problem.required_parts.length > 0 && (
          <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
            <h2 className="text-xl font-bold text-blue-900 mb-4">
              📦 Parts You Need to Buy
            </h2>
            <div className="space-y-4">
              {problem.required_parts.map((part, idx) => (
                <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between bg-white p-4 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                  <span className="font-medium text-gray-800 mb-3 sm:mb-0 text-lg">
                    {part.name}
                  </span>
                  <a
                    href={getAmazonLink(part.search_query)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-sm font-bold rounded-lg text-white bg-orange-500 hover:bg-orange-600 shadow-sm transition-colors whitespace-nowrap"
                  >
                    View Exact Part on Amazon &rarr;
                  </a>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-400 mt-4 text-center">
              We recommend genuine or high-rated compatible parts. As an Amazon Associate we earn from qualifying purchases.
            </p>
          </div>
        )}

        {/* 潜在原因 (移到底部) */}
        <div className="mt-10 pt-8 border-t border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Possible Causes</h3>
          <ul className="list-disc list-inside text-gray-600 space-y-1">
            {problem.possible_causes.map((cause, idx) => (
              <li key={idx}>{cause}</li>
            ))}
          </ul>
        </div>

        {/* FAQ Section (Boosts SEO) */}
        {data.faqs && data.faqs.length > 0 && (
          <div className="mt-12 pt-10 border-t-4 border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h3>
            <div className="space-y-6">
              {data.faqs.map((faq, idx) => (
                <div key={idx}>
                  <h4 className="font-bold text-gray-800 text-lg mb-2">{faq.question}</h4>
                  <p className="text-gray-600 leading-relaxed bg-gray-50 p-4 rounded-lg">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 免责声明 (增加正规感) */}
        <div className="mt-12 pt-6 border-t border-gray-100 text-xs text-gray-400 text-center leading-relaxed">
          <p>Disclaimer: We provide DIY guides based on manufacturer manuals. We are not responsible for any damage caused during repair. Always unplug your device first. If unsure, contact professional repair services.</p>
        </div>

      </article>

      {/* Sticky Mobile Buy Button */}
      {problem.required_parts.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)] md:hidden z-50">
          <a
            href={getAmazonLink(problem.required_parts[0].search_query)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center w-full px-6 py-4 bg-orange-500 text-white font-bold text-lg rounded-xl shadow-lg animate-pulse"
          >
            Check Price on Amazon &rarr;
          </a>
        </div>
      )}
    </div>
  );
}
