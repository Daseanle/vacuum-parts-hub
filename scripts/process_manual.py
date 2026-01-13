import pdfplumber
import json
from openai import OpenAI
import os

# 这里填你的 OpenAI Key，或者设置环境变量 OPENAI_API_KEY
client = OpenAI(api_key="sk-xxxxxxxxx") 

def extract_text_from_pdf(pdf_path):
    """从PDF中提取所有文本"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # 简单的清洗，去掉页眉页脚
            text += page.extract_text() + "\n"
    return text

def analyze_with_gpt(raw_text, brand, model):
    """把乱糟糟的文本喂给 GPT，让它拉出这就是我们要的 JSON"""
    
    # 提示词工程 (Prompt Engineering) - 这是核心资产
    prompt = f"""
    You are a professional vacuum cleaner repair expert.
    I have the raw text from the user manual of a {brand} {model}.
    
    Your goal is to extract the "Troubleshooting" or "Problem Solving" section and structure it into JSON.
    
    Requirements:
    1. Identify specific problems (e.g., "Vacuum not picking up debris", "Brush roll not spinning").
    2. Extract the symptoms and solution steps.
    3. Suggest parts that might need replacement (e.g., Filter, Belt, Hose) based on the solution.
    4. Improve the language to be SEO-friendly and clear.
    
    Return ONLY valid JSON with this structure:
    {{
      "brand": "{brand}",
      "model": "{model}",
      "problems": [
        {{
          "id": "slug-style-id-for-url", 
          "title": "Problem Title",
          "description": "Short description of the issue.",
          "possible_causes": ["Cause 1", "Cause 2"],
          "steps": ["Step 1", "Step 2", "Step 3"],
          "required_parts": ["Filter", "Belt"] 
        }}
      ]
    }}
    
    Here is the manual text (truncated for token limit if needed):
    {raw_text[:15000]} 
    """
    
    # 如果说明书特别长，可能需要只截取 Troubleshooting 的部分，或者用 GPT-4-Turbo/128k 模型
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k", # 或者 gpt-4-turbo
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={ "type": "json_object" }
    )
    
    return response.choices[0].message.content

# --- 执行主程序 ---
if __name__ == "__main__":
    # 1. 你的 PDF 路径 (把下载的 PDF 放在这里)
    pdf_file = "Shark_NV352.pdf" 
    brand_name = "Shark"
    model_name = "Navigator Lift-Away NV352"
    
    print(f"正在读取 {pdf_file}...")
    text_content = extract_text_from_pdf(pdf_file)
    
    print("正在调用 AI 进行清洗 (这可能需要几秒钟)...")
    json_output = analyze_with_gpt(text_content, brand_name, model_name)
    
    # 2. 保存结果
    output_filename = f"../data/{brand_name.lower()}-{model_name.replace(' ', '-').lower()}.json"
    
    # 确保 data 目录存在
    os.makedirs("../data", exist_ok=True)
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(json_output)
        
    print(f"成功！数据已保存到 {output_filename}")
