import { getAllModelSlugs } from '@/lib/vacuum-data';
import { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://vacuumpartshub.com'; // 你的域名
  
  // 1. 获取所有型号的页面
  const models = await getAllModelSlugs();
  
  // 2. 生成动态路由的 Sitemap
  const modelUrls = models.map((item) => ({
    url: `${baseUrl}/guide/${item.model}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));

  // 3. 加上首页
  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    ...modelUrls,
  ];
}
