import os
import json
import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
app = Flask(__name__)
CORS(app)

# Note: We no longer initialize the client here to prevent startup crashes if .env is missing.

def gh_get(endpoint, token):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token: 
        headers["Authorization"] = f"token {token}"
    else: 
        headers["Authorization"] = f"token {os.environ.get('GITHUB_TOKEN', '')}"
    
    res = requests.get(f"https://api.github.com{endpoint}", headers=headers)
    return res.json() if res.ok else None

def get_file_content(owner, repo, path, token):
    data = gh_get(f"/repos/{owner}/{repo}/contents/{path}", token)
    if data and data.get('content'):
        return base64.b64decode(data['content']).decode('utf-8', errors='ignore')
    return ""

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    owner, repo = data.get('owner'), data.get('repo')
    token = data.get('token')
    
    # 1. Get API key from popup, fallback to .env
    api_key = data.get('groq_key') or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return jsonify({"error": "Missing API key. Please add it in the extension popup or .env file."}), 400

    # 2. Initialize client dynamically with the valid key
    local_client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    # 3. Fetch Raw Data
    info = gh_get(f"/repos/{owner}/{repo}", token)
    if not info: return jsonify({"error": "Repo not found"}), 404
    
    topics_data = gh_get(f"/repos/{owner}/{repo}/topics", token)
    topics = topics_data.get('names', []) if topics_data else []
    
    tree_data = gh_get(f"/repos/{owner}/{repo}/git/trees/main?recursive=1", token)
    file_tree = tree_data.get('tree', []) if tree_data else []
    
    file_paths = [f['path'] for f in file_tree if f['type'] == 'blob'][:80] 
    
    readme_data = gh_get(f"/repos/{owner}/{repo}/readme", token)
    readme_text = ""
    if readme_data and readme_data.get('content'):
        readme_text = base64.b64decode(readme_data['content']).decode('utf-8', errors='ignore')[:3500]

    # 4. The AI Prompt
    prompt = f"""
    Analyze this GitHub repository based on its file structure and README.
    Repository: {owner}/{repo}
    Description: {info.get('description') or 'None'}
    Topics: {', '.join(topics)}
    Primary Language: {info.get('language') or 'Unknown'}
    
    File Structure (Sample):
    {json.dumps(file_paths, indent=2)}
    
    README Content:
    {readme_text}
    
    Return a STRICT JSON object (no markdown formatting). Use these exact keys:
    - "summary": A 1-2 sentence "TL;DR" for a developer.
    - "tags": An array of 3 to 5 highly relevant, specific tags (e.g., "Web Scraping", "UI Library", "DevOps"). NEVER use "Repository" or "Open Source".
    - "os_support": An array of supported OS (e.g., ["Linux", "macOS", "Windows", "Web", "Cross-platform"]).
    - "frameworks": An array of 3 to 5 specific frameworks, libraries, or tools (e.g., ["React", "Docker", "Tailwind"]). DO NOT list base languages.
    - "setup_complexity": "Easy", "Medium", or "Hard".
    - "architecture": An array of 1-2 inferred patterns (e.g., ["Monorepo", "Microservices", "MVC", "Serverless"]).
    - "deployment_targets": An array of 1-2 inferred targets (e.g., ["Docker", "Vercel", "AWS", "Static Site"]).
    - "entry_points": An array of 1-3 specific file paths where a developer should start reading (e.g., ["src/main.py", "app/index.ts"]).
    """
    
    try:
        response = local_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "You are an expert software architect. You MUST respond with a STRICT JSON object. Do not include markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        clean_text = response.choices[0].message.content.strip().replace('```json', '').replace('```', '').strip()
        ai_data = json.loads(clean_text)
    except Exception as e:
        print(f"AI Error: {e}")
        ai_data = {
            "summary": info.get('description') or 'Analysis failed.',
            "tags": [info.get('language') or 'Code', 'Project'],
            "os_support": ['Cross-platform'],
            "frameworks": [info.get('language') or 'Unknown'],
            "setup_complexity": "Medium",
            "architecture": ["Standard"],
            "deployment_targets": ["Standard"],
            "entry_points": ["Standard"]
        }

    # Safety fallbacks
    if not ai_data.get('tags') or 'unknown' in str(ai_data['tags']).lower():
        ai_data['tags'] = [info.get('language') or 'Code', 'Project']
    if not ai_data.get('os_support') or 'unknown' in str(ai_data['os_support']).lower():
        ai_data['os_support'] = ['Cross-platform']

    # 5. Related Repos
    related = []
    if topics:
        topic_query = " ".join([f"topic:{t}" for t in topics[:2]])
        search_q = f"{topic_query} stars:>100 -repo:{owner}/{repo}"
    else:
        desc_words = (info.get('description') or '').split()[:3]
        search_q = f"{' '.join(desc_words)} language:{info.get('language') or 'code'} stars:>100 -repo:{owner}/{repo}"
    
    search_res = gh_get(f"/search/repositories?q={requests.utils.quote(search_q)}&sort=stars&per_page=4", token)
    if search_res and 'items' in search_res:
        for item in search_res['items'][:4]:
            related.append({"name": item['full_name'], "stars": item['stargazers_count'], "url": item['html_url']})

    # 6. Return JSON
    return jsonify({
        "summary": ai_data.get("summary"),
        "tags": ai_data.get("tags", []),
        "os_support": ai_data.get("os_support", []),
        "frameworks": ai_data.get("frameworks", []),
        "setup_complexity": ai_data.get("setup_complexity", "Medium"),
        "architecture": ai_data.get("architecture", []),
        "deployment_targets": ai_data.get("deployment_targets", []),
        "entry_points": ai_data.get("entry_points", []),
        "related_repos": related
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)