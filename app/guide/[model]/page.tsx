import { getModelData, getAllModelSlugs } from '@/lib/vacuum-data';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

export async function generateStaticParams() {
  return await getAllModelSlugs();
}

// 增加 SEO 标题优化
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

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 font-sans">
      <nav className="text-sm text-gray-500 mb-4">
        <Link href="/" className="hover:text-blue-600">Home</Link> &gt; {data.brand} &gt; {data.model}
      </nav>

      <header className="mb-12 text-center">
        {/* --- 图片展示区域 Start --- */}
        {data.image_url && (
          <div className="flex justify-center mb-8">
            <div className="relative w-64 h-64 bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <img
                src={data.image_url}
                alt={`${data.brand} ${data.model}`}
                className="w-full h-full object-contain hover:scale-105 transition-transform duration-300"
              />
            </div>
          </div>
        )}
        {/* --- 图片展示区域 End --- */}

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
