#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Vacuum Parts Hub - Automated SEO Content Generator
---------------------------------------------------
Target: High-Intent Troubleshooting & Parts Keywords
Output: JSON Data Files (consumed by Next.js)
Daily Volume: 5-10 Pages
"""

import os
import sys
import json
import random
import time
import subprocess
from datetime import datetime
from pathlib import Path

# =================CONFIGURATION=================
PROJECT_ROOT = Path("/Volumes/MOVESPEED/下载/AIcode/vacuum-parts-hub")
DATA_DIR = PROJECT_ROOT / "data"
LOG_FILE = PROJECT_ROOT / "logs" / "seo_generation.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Top Vacuum Brands & Models for mix-and-match
BRANDS = {
    "Dyson": ["V8 Animal", "V10 Absolute", "V11 Torque Drive", "V15 Detect", "Ball Animal 2"],
    "Shark": ["Navigator Lift-Away", "Rotator Professional", "Vertex DuoClean", "Rocket Pet Pro"],
    "Bissell": ["CrossWave", "Little Green", "CleanView Swivel", "Pet Hair Eraser"],
    "Hoover": ["WindTunnel 3", "PowerDash Pet", "SmartWash Automatic"],
    "iRobot": ["Roomba j7+", "Roomba s9+", "Braava Jet m6"]
}

# High-Intent SEO Topics (Schema-based)
TOPICS = [
    # 1. Troubleshooting (Focus: "Why is my...", "How to fix...")
    {
        "type": "troubleshooting",
        "title_template": "Why Your {model} Is {problem} (And How to Fix It)",
        "slug_template": "{brand}-{model}-is-{problem}-fix",
        "variables": {
            "problem": ["Not Suctioning", "Smelling Burnt", "Making Loud Noise", "Blinking Red Light", "Not Charging", "Spitting Out Dust"]
        }
    },
    # 2. Part Replacement Guides (Focus: "Replacement", "Change")
    {
        "type": "guide",
        "title_template": "How to Replace the {part} on a {model}",
        "slug_template": "replace-{part}-{brand}-{model}",
        "variables": {
            "part": ["HEPA Filter", "Brush Roll", "Battery", "Drive Belt", "Dust Bin"]
        }
    },
    # 3. Maintenance (Focus: "Cleaning", "Washing")
    {
        "type": "maintenance",
        "title_template": "Step-by-Step: Cleaning the {part} of Your {model}",
        "slug_template": "how-to-clean-{brand}-{model}-{part}",
        "variables": {
            "part": ["Filters", "Cyclone Assembly", "Roller Head", "Soft Roller"]
        }
    }
]

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    print(formatted_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

# =================CONTENT GENERATION=================

def generate_content(brand, model, topic, title):
    """Generates structured JSON content matching the existing schema."""
    
    # 1. Define the specific problem based on topic
    problem_type = topic['variables'].get('problem', ['General Issue'])[0] if 'problem' in topic['variables'] else 'Maintenance'
    part_type = topic['variables'].get('part', ['Parts'])[0] if 'part' in topic['variables'] else 'Part'
    
    # 2. Construct SEO Keywords
    keywords = [
        f"{model} {problem_type}",
        f"Fix {model} {problem_type}",
        f"{brand} {model} troubleshooting",
        f"{model} {part_type} replacement",
        f"how to manual for {model}"
    ]
    
    # 3. Generate structured problem data
    # This mimics the "problems" array in existing JSONs
    problem_entry = {
        "id": f"{problem_type.lower().replace(' ', '-')}-issue",
        "title": f"Fixing: {problem_type} on {model}",
        "description": f"Comprehensive guide to resolving {problem_type.lower()} issues. If your {model} is acting up, followed these steps.",
        "possible_causes": [
            f"Worn out {part_type}",
            "Blockage in the airway",
            "Electrical connection failure",
            "Sensor malfunction"
        ],
        "solution_steps": [
            "Turn off and unplug the device.",
            f"Inspect the {part_type} for visible damage or debris.",
            "Clean all contact points using a dry cloth.",
            "Reset the machine by holding the power button for 10 seconds.",
            f"If the issue persists, replace the {part_type}."
        ],
        "required_parts": [
            {
                "name": f"{model} {part_type}",
                "search_query": f"{model} {part_type} replacement"
            }
        ]
    }
    
    # 4. Final JSON Structure
    data = {
        "brand": brand,
        "model": f"{model} - {problem_type}", # Acts as the page H1
        "manual_pdf": f"{model.lower().replace(' ', '-')}-manual.pdf",
        "seo_keywords": keywords,
        "auto_generated": True,
        "generated_date": datetime.now().isoformat(),
        "source_keyword": f"{model} {problem_type}",
        "problem_type": problem_type.lower(),
        "trending_score": random.randint(50, 90),
        "problems": [problem_entry]
    }
    
    return data

# =================GIT & NOTIFICATION=================

def run_shell(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"❌ Command failed: {command}\nError: {e.stderr}")
        return False, e.stderr

import urllib.request
import urllib.parse

def send_telegram_notification(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        log("⚠️ Telegram credentials not found. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    headers = {'Content-Type': 'application/json'}
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                log("✅ Telegram notification sent.")
            else:
                log(f"❌ Failed to send Telegram notification: {response.read().decode('utf-8')}")
    except Exception as e:
        log(f"❌ Error sending Telegram notification: {e}")

def git_commit_and_push(generated_files):
    log("📦 Starting Git Push sequence...")
    run_shell(f"git add .")
    msg = f"SEO Auto-Gen: {len(generated_files)} new vacuum guides"
    run_shell(f"git commit -m '{msg}'")
    success, _ = run_shell("git push")
    
    if success:
        log("✅ Git Push Successful!")
        # Send Success Notification
        report = f"✅ *Vacuum Parts Hub Auto-SEO Success*\nGenerated {len(generated_files)} new guides:\n" + "\n".join([f"• {f}" for f in generated_files])
        send_telegram_notification(report)
    else:
        log("❌ Git Push Failed.")
        send_telegram_notification("❌ *Vacuum Parts Hub Auto-SEO Failed* during git push.")
    return success

# =================MAIN EXECUTION=================

def main():
    log("🚀 Starting Vacuum Hub SEO Generator...")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    generated_count = 0
    generated_files = []
    
    # Generate 5 pages per run
    while generated_count < 5:
        # 1. Random Selection
        brand = random.choice(list(BRANDS.keys()))
        model = random.choice(BRANDS[brand])
        topic = random.choice(TOPICS)
        
        # 2. Build Filename (Slug)
        # We start with model name
        slug_base = f"{model.lower().replace(' ', '-')}"
        
        # Add problem suffix
        problem = topic["variables"].get("problem", ["guide"])[0] 
        # Or part
        part = topic["variables"].get("part", [""])[0]
        
        suffix = problem.lower().replace(' ', '-') if problem != "guide" else f"replace-{part.lower().replace(' ', '-')}"
        
        slug = f"{brand.lower()}-{slug_base}-{suffix}"
        
        # Inject variable for title generation
        topic['variables']['problem'] = [problem]
        topic['variables']['part'] = [part]
        
        title = f"{brand} {model} {problem}" # Simple internal title for logging
        
        filename = f"{slug}.json"
        filepath = DATA_DIR / filename
        
        if filepath.exists():
            continue
            
        # 3. Generate
        log(f"  ✍️ Generating: {title}")
        content_data = generate_content(brand, model, topic, title)
        
        # 4. Save
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
            
        generated_count += 1
        generated_files.append(title)
        time.sleep(1)

    log(f"🎉 Generated {generated_count} guides.")
    
    if generated_count > 0:
        git_commit_and_push(generated_files)

if __name__ == "__main__":
    main()

