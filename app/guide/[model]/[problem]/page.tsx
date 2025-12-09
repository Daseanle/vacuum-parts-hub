import { getModelData, getAllModelSlugs } from '@/lib/vacuum-data';
import Link from 'next/link';
import { notFound } from 'next/navigation';

export async function generateStaticParams() {
  const paths = await getAllModelSlugs();
  // 这里简化处理，实际生产环境应该遍历所有 problem 生成静态路径
  return []; 
}

// 生成亚马逊搜索链接的工具
function getAmazonLink(query: string) {
  const tag = "vacuumhub-20"; // 以后替换成你自己的 Amazon Affiliate ID
  return `https://www.amazon.com/s?k=${encodeURIComponent(query)}&tag=${tag}`;
}

export default async function ProblemPage({ 
  params 
}: { 
  params: { model: string; problem: string } 
}) {
  const data = await getModelData(params.model);
  
  if (!data) return notFound();

  const problem = data.problems.find(p => p.id === params.problem);
  if (!problem) return notFound();

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      {/* 导航 */}
      <Link 
        href={`/guide/${params.model}`} 
        className="text-blue-600 hover:underline mb-6 inline-block font-medium"
      >
        &larr; Back to {data.model} Overview
      </Link>

      <article className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {problem.title}
          </h1>
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
            <p className="font-bold text-yellow-800">Symptoms:</p>
            <p className="text-yellow-700">{problem.description}</p>
          </div>

          {/* 解决方案步骤 */}
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">How to Fix It</h2>
            <ol className="list-decimal list-outside ml-5 space-y-4">
              {problem.solution_steps.map((step, idx) => (
                <li key={idx} className="text-lg text-gray-700 pl-2">
                  {step}
                </li>
              ))}
            </ol>
          </div>

          {/* 核心赚钱模块：所需配件 */}
          {problem.required_parts.length > 0 && (
            <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
              <h2 className="text-xl font-bold text-blue-900 mb-4 flex items-center">
                🔧 Parts You May Need
              </h2>
              <div className="space-y-4">
                {problem.required_parts.map((part, idx) => (
                  <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between bg-white p-4 rounded-lg shadow-sm">
                    <span className="font-medium text-gray-800 mb-2 sm:mb-0">
                      {part.name}
                    </span>
                    <a 
                      href={getAmazonLink(part.search_query)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-500 hover:bg-orange-600 shadow-sm transition-colors whitespace-nowrap"
                    >
                      Check Price on Amazon
                    </a>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-4 text-center">
                As an Amazon Associate we earn from qualifying purchases.
              </p>
            </div>
          )}

          {/* 潜在原因 */}
          <div className="mt-10 pt-8 border-t border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Possible Causes</h3>
            <ul className="list-disc list-inside text-gray-600">
              {problem.possible_causes.map((cause, idx) => (
                <li key={idx}>{cause}</li>
              ))}
            </ul>
          </div>
        </div>
      </article>
    </div>
  );
}
