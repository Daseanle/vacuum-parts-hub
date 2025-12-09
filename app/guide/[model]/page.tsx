import { getModelData, getAllModelSlugs } from '@/lib/vacuum-data';
import Link from 'next/link';
import { notFound } from 'next/navigation';

// 静态生成路径
export async function generateStaticParams() {
  return await getAllModelSlugs();
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

      <header className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
          {data.brand} {data.model} Repair Guide
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
            <div className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow bg-white h-full">
              <h2 className="text-xl font-bold text-blue-600 group-hover:underline mb-2">
                {problem.title}
              </h2>
              <p className="text-gray-600 line-clamp-2 text-sm">
                {problem.description}
              </p>
              <div className="mt-4 text-sm text-gray-400 font-medium">
                View Solution &rarr;
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
