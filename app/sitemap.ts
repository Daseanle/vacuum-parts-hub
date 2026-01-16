import { MetadataRoute } from 'next';
import { getAllModelSlugs, getModelData } from '@/lib/vacuum-data';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://vacuumpartshub.com';

  const slugs = await getAllModelSlugs();
  const guideUrls: MetadataRoute.Sitemap = [];

  for (const item of slugs) {
    const data = await getModelData(item.model);
    if (!data) continue;

    // Index the specific problem solution pages (High Value)
    for (const problem of data.problems) {
      guideUrls.push({
        url: `${baseUrl}/guide/${item.model}/${problem.id}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.9,
      });
    }

    // Optionally index the hub page if it has multiple problems
    if (data.problems.length > 1) {
      guideUrls.push({
        url: `${baseUrl}/guide/${item.model}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.7,
      });
    }
  }

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    ...guideUrls,
  ];
}
