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
  manual_pdf: string;
  seo_keywords: string[];
  problems: Problem[];
}

export async function getAllModelSlugs() {
  // 如果 data 目录不存在，防止报错
  if (!fs.existsSync(dataDirectory)) {
    return [];
  }
  const fileNames = fs.readdirSync(dataDirectory);
  return fileNames.map((fileName) => {
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
