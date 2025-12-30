import { MetadataRoute } from 'next';
import vacuums from '@/data/vacuums.json'; // 读取刚才的 JSON

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://vacuumpartshub.com';

  const vacuumUrls = vacuums.map((vacuum) => ({
    url: `${baseUrl}/dyson/${vacuum.slug}`,
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
    ...vacuumUrls,
  ];
}
