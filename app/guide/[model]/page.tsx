import { getModelData, getAllModelSlugs } from '@/lib/vacuum-data';
import Link from 'next/link';
import { notFound } from 'next/navigation';

export async function generateStaticParams() {
  const paths = await getAllModelSlugs();
  return paths.map((path) => path.params);
}

export default async function ModelPage({ params }: { params: { model: string } }) {
  const data = await getModelData(params.model);

  if (!data) {
    return notFound();
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* 面包屑导航 */}
      <nav className="text-sm text-gray-500 mb-4">
        <Link href="/" className="hover:underline">Home</Link> &gt; {data.brand} &gt; {data.model}
      </nav>

      <header className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
          {data.brand} {data.model} Repair Guide
        </h1>
        <p className="text-xl text-gray-600">
          Select your problem below to find the solution and replacement parts.
        </p>
      </header>

      {/* 问题列表 - 核心入口 */}
      <div className="grid gap-6 md:grid-cols-2">
        {data.problems.map((problem) => (
          <Link 
            key={problem.id} 
            href={`/guide/${params.model}/${problem.id}`}
            className="block group"
          >
            <div className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow bg-white h-full">
              <h2 className="text-xl font-bold text-blue-600 group-hover:underline mb-2">
                {problem.title}
              </h2>
              <p className="text-gray-600 line-clamp-2">
                {problem.description}
              </p>
              <div className="mt-4 text-sm text-gray-400 flex items-center">
                View Solution &rarr;
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* SEO 关键词堆砌区 (对用户不可见但对爬虫友好) */}
      <div className="mt-16 pt-8 border-t border-gray-100">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">
          Common Searches
        </h3>
        <div className="flex flex-wrap gap-2">
          {data.seo_keywords.map((kw, idx) => (
            <span key={idx} className="bg-gray-100 text-gray-500 px-3 py-1 rounded-full text-xs">
              {kw}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
