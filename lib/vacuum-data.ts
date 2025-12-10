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
}

// lib/vacuum-data.ts 的 getAllModelSlugs 必须长这样：
export async function getAllModelSlugs() {
  if (!fs.existsSync(dataDirectory)) {
    return [];
  }
  const fileNames = fs.readdirSync(dataDirectory);
  return fileNames.map((fileName) => {
    return {
      model: fileName.replace(/\.json$/, ''), // 注意：这里直接返回 model，不要包在 params 里
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
