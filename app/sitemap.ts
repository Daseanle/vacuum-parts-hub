import { MetadataRoute } from 'next';
import { getAllModelSlugs } from '@/lib/vacuum-data';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://vacuumpartshub.com';

  // 获取所有真实存在的指南页面 (从 data/*.json 如果是 getAllModelSlugs 读取目录)
  const slugs = await getAllModelSlugs();

  const guideUrls = slugs.map((item) => ({
    url: `${baseUrl}/guide/${item.model}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));

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
