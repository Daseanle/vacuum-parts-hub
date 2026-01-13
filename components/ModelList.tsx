"use client"; // 这一行告诉 Next.js 这是客户端组件

import { useState } from "react";
import Link from "next/link";

// 定义数据类型
interface ModelListProps {
  models: { model: string }[];
}

export default function ModelList({ models }: ModelListProps) {
  const [query, setQuery] = useState("");

  // 核心逻辑：根据用户输入过滤列表
  const filteredModels = models.filter((item) =>
    item.model.toLowerCase().replace(/-/g, " ").includes(query.toLowerCase())
  );

  return (
    <div className="w-full max-w-2xl">
      {/* 搜索框 */}
      <div className="mb-8 relative">
        <input
          type="text"
          placeholder="Search your vacuum model (e.g. Dyson V8)..."
          className="w-full p-4 pl-12 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-lg"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        {/* 搜索图标 */}
        <svg
          className="absolute left-4 top-1/2 transform -translate-y-1/2 h-6 w-6 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* 结果列表 */}
      <div className="grid gap-4">
        <h2 className="text-xl font-bold text-gray-800 mb-2">
          {filteredModels.length} Guides Found:
        </h2>
        
        {filteredModels.length > 0 ? (
          filteredModels.map((item) => (
            <Link
              key={item.model}
              href={`/guide/${item.model}`}
              className="group p-6 bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-200 transition-all flex justify-between items-center"
            >
              <span className="text-lg font-medium text-blue-600 capitalize group-hover:text-blue-800">
                {item.model.replace(/-/g, " ")}
              </span>
              <span className="text-gray-400 group-hover:translate-x-1 transition-transform">
                &rarr;
              </span>
            </Link>
          ))
        ) : (
          <div className="text-center p-8 bg-gray-100 rounded-lg text-gray-500">
            No guides found for "{query}". <br />
            <span className="text-sm">Try searching for the brand (e.g. Shark)</span>
          </div>
        )}
      </div>
    </div>
  );
}
