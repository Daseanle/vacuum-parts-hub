import os
import json
import random
from pathlib import Path

# Paths
base_dir = Path("/Volumes/MOVESPEED/下载/AIcode/vacuum-parts-hub")
data_dir = base_dir / "data"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_faqs(data):
    brand = data.get('brand', 'Generic')
    model = data.get('model', 'Vacuum').split(' - ')[0] # Clean up model name if it has problem attached
    
    # Try to extract specific part info from the first problem
    problem = data['problems'][0] if data.get('problems') else None
    problem_type = "issue"
    part_name = "part"
    
    if problem:
        if "battery" in problem.get('title', '').lower():
            problem_type = "battery"
            part_name = "battery"
        elif "filter" in problem.get('title', '').lower():
            problem_type = "filter"
            part_name = "filter"
        elif "suction" in problem.get('title', '').lower():
            problem_type = "suction"
            part_name = "filter or seal"
            
    # Generate generic but relevant FAQs
    return [
        {
            "question": f"Is it worth fixing the {problem_type} on a {model}?",
            "answer": f"Yes. A replacement {part_name} typically costs significantly less than a new ${random.randint(300, 600)} vacuum, and extending the life of your {brand} is eco-friendly."
        },
        {
            "question": f"How do I know if my {model} needs a new {part_name}?",
            "answer": f"Common signs include {random.choice(['reduced performance', 'strange noises', 'intermittent power'])} and the device failing to complete a cleaning cycle."
        },
        {
            "question": f"Can I replace the {part_name} on my {model} myself?",
            "answer": "Yes, this is a user-serviceable repair. Most replacements generally require just a screwdriver and about 10-20 minutes of time."
        }
    ]

def main():
    print(f"🧹 Starting retro-fill for VacuumHub data in {data_dir}...")
    
    files = [f for f in os.listdir(data_dir) if f.endswith('.json') and f not in ['vacuums.json', 'sharks.json', 'bissells.json']]
    count = 0
    
    for filename in files:
        filepath = data_dir / filename
        try:
            data = load_json(filepath)
            
            # Check if FAQs already exist
            if 'faqs' in data and data['faqs']:
                # print(f"Skipping {filename} (FAQs exist)")
                continue
                
            # Generate and inject FAQs
            data['faqs'] = generate_faqs(data)
            
            # Save back
            save_json(filepath, data)
            count += 1
            if count % 50 == 0:
                print(f"✅ Processed {count} files...")
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

    print(f"🎉 Complete! Added FAQs to {count} files.")

if __name__ == "__main__":
    main()
