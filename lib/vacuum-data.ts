import fs from 'fs';
import path from 'path';

const dataDirectory = path.join(process.cwd(), 'data');

// 定义数据类型，让代码知道 JSON 长什么样
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
  manual_pdf: string;
  seo_keywords: string[];
  problems: Problem[];
}

// 获取所有型号的 Slug (用于生成静态路径)
export async function getAllModelSlugs() {
  const fileNames = fs.readdirSync(dataDirectory);
  return fileNames.map((fileName) => {
    return {
      params: {
        model: fileName.replace(/\.json$/, ''),
      },
    };
  });
}

// 根据型号 Slug 获取具体数据
export async function getModelData(slug: string): Promise<VacuumManual | null> {
  const fullPath = path.join(dataDirectory, `${slug}.json`);
  if (!fs.existsSync(fullPath)) {
    return null;
  }
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  return JSON.parse(fileContents);
}
