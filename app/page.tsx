import Link from 'next/link';
import { getAllModelSlugs } from '@/lib/vacuum-data';

export default async function Home() {
  // 获取所有已生成的指南
  const guides = await getAllModelSlugs();

  return (
    <main className="flex min-h-screen flex-col items-center p-24">
      <h1 className="text-6xl font-bold text-blue-600 mb-8">VacuumPartsHub</h1>
      <p className="text-xl mb-12 text-gray-600">The AI-Powered Repair Guide & Parts Locator.</p>
      
      <div className="grid gap-4 w-full max-w-2xl">
        <h2 className="text-2xl font-bold">Available Guides:</h2>
        {guides.length > 0 ? (
          guides.map((item) => (
            <Link 
              key={item.model}
              href={`/guide/${item.model}`}
              className="p-6 bg-white rounded-lg shadow hover:shadow-md border border-gray-200 block"
            >
              <span className="text-lg font-medium text-blue-600 capitalize">
                {item.model.replace(/-/g, ' ')}
              </span>
            </Link>
          ))
        ) : (
          <p>No guides found. Please check data folder.</p>
        )}
      </div>
    </main>
  );
}
