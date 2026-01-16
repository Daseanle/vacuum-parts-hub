import fs from 'fs';
import path from 'path';

const dataDirectory = path.join(process.cwd(), 'data');

export interface VacuumPart {
  name: string;
  search_query: string;
}

export interface Problem {
  id: string;
  title: string;
  description: string;
  possible_causes: string[];
  solution_steps: string[];
  required_parts: VacuumPart[];
}

export interface VacuumManual {
  brand: string;
  model: string;
  image_url: string; // <--- 必须加上这一行！
  manual_pdf: string;
  seo_keywords: string[];
  problems: Problem[];
  faqs?: { question: string; answer: string; }[];
}

// lib/vacuum-data.ts 的 getAllModelSlugs 必须长这样：
// 获取所有型号的 Slug (用于生成静态路径)
export async function getAllModelSlugs() {
  // 如果 data 目录不存在，防止报错
  if (!fs.existsSync(dataDirectory)) {
    return [];
  }
  const fileNames = fs.readdirSync(dataDirectory);

  // 关键修改：过滤掉 vacuums.json 以及未来可能添加的 sharks.json 等聚合文件
  // 我们只保留那些针对单个型号的维修指南 JSON
  const repairGuideFiles = fileNames.filter(fileName => {
    // 排除列表：在这里添加不想被 /guide/ 路径读取的文件
    const excludeList = ['vacuums.json', 'sharks.json', 'bissells.json'];
    return !excludeList.includes(fileName);
  });

  return repairGuideFiles.map((fileName) => {
    return {
      model: fileName.replace(/\.json$/, ''),
    };
  });
}

export async function getModelData(slug: string): Promise<VacuumManual | null> {
  const fullPath = path.join(dataDirectory, `${slug}.json`);
  if (!fs.existsSync(fullPath)) {
    return null;
  }
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  return JSON.parse(fileContents);
}
