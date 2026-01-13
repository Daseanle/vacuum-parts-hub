import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: '/private/', // 这里可以填你不希望被收录的路径，目前没有，留个样子或者删掉都行
    },
    sitemap: 'https://vacuumpartshub.com/sitemap.xml',
  };
}
