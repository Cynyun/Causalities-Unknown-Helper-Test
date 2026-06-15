import asyncio
import aiohttp
import json
import os
import re

def load_config():
    """从 config.json 加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def fetch_page_content(session, base_url, params):
    """获取页面内容（通用 API 调用）"""
    print(f"[Fetching] URL: {base_url}")
    print(f"[Params] {params}")
    
    async with session.get(base_url, params=params) as response:
        if response.status != 200:
            print(f"[Error] HTTP status: {response.status}")
            return None
        
        data = await response.json()
        return data

async def fetch_with_continue(session, base_url, params):
    """处理分页的 API 调用"""
    all_results = []
    continue_params = {}
    
    while True:
        request_params = {**params, **continue_params}
        
        data = await fetch_page_content(session, base_url, request_params)
        
        if not data:
            break
        
        if "query" in data:
            if "pages" in data["query"]:
                all_results.extend(data["query"]["pages"].values())
            elif "categorymembers" in data["query"]:
                all_results.extend(data["query"]["categorymembers"])
        
        if "continue" in data:
            continue_params = data["continue"]
            print(f"[Continue] Fetching next batch...")
            await asyncio.sleep(1)
        else:
            break
    
    return all_results

def process_redirects(pages_data, redirects_list):
    """处理重定向页面"""
    redirect_targets = set(r['to'] for r in redirects_list)
    
    pages_to_remove = []
    for pageid, pageinfo in pages_data.items():
        title = pageinfo.get("title", "")
        revisions = pageinfo.get("revisions", [])
        
        if revisions:
            content = revisions[0].get("*", "")
            is_redirect = content.strip().startswith("#REDIRECT")
            
            if is_redirect:
                is_target = any(r['to'] == title for r in redirects_list)
                if not is_target:
                    pages_to_remove.append(pageid)
    
    for pageid in pages_to_remove:
        if pageid in pages_data:
            del pages_data[pageid]
    
    return pages_data

async def main():
    config = load_config()
    base_url = config["base_url"]
    entry_pages = config["entry_pages"]
    output_dir = config["output_dir"]
    
    os.makedirs(output_dir, exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        raw_results = {}
        
        print("=== Layer 1: Fetching entry pages ===")
        
        for entry in entry_pages:
            page_name = entry["name"]
            api_type = entry["api_type"]
            params = entry["params"]
            
            print(f"\n--- Fetching: {page_name} ({api_type}) ---")
            
            if api_type == "revisions":
                data = await fetch_page_content(session, base_url, params)
                
                if data:
                    redirects = data.get("query", {}).get("redirects", [])
                    pages = data["query"].get("pages", {})
                    processed_pages = process_redirects(pages, redirects)
                    
                    raw_results[page_name.replace("/", "_")] = {
                        "batchcomplete": "",
                        "query": {
                            "pages": processed_pages
                        }
                    }
            
            elif api_type == "categorymembers":
                members = await fetch_with_continue(session, base_url, params)
                
                raw_results[page_name.replace("/", "_")] = {
                    "batchcomplete": "",
                    "query": {
                        "categorymembers": members
                    }
                }
        
        raw_file = f"{output_dir}/l1_raw.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_results, f, ensure_ascii=False, indent=2)
        print(f"\n[Saved] Raw data to {raw_file}")

if __name__ == "__main__":
    asyncio.run(main())