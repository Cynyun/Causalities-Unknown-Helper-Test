import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_raw_to_wiki():
    config = load_config()
    output_dir = config["output_dir"]
    entry_pages = config["entry_pages"]
    
    raw_file = f"{output_dir}/l1_raw.json"
    
    if not os.path.exists(raw_file):
        print(f"[Error] Raw file not found: {raw_file}")
        return None
    
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    os.makedirs(f"{output_dir}/wiki_docs", exist_ok=True)
    
    wiki_files_generated = []
    
    for entry in entry_pages:
        page_name = entry["name"]
        api_type = entry["api_type"]
        key_name = page_name.replace("/", "_")
        
        if key_name not in raw_data:
            print(f"[Warning] No data found for {page_name}")
            continue
        
        if api_type == "revisions":
            pages = raw_data[key_name]["query"].get("pages", {})
            
            for pageid, pageinfo in pages.items():
                if "missing" in pageinfo:
                    continue
                
                title = pageinfo.get("title", "Unknown")
                revisions = pageinfo.get("revisions", [])
                
                if revisions:
                    content = revisions[0].get("*", "")
                    
                    filename = title.replace("/", "_").replace(" ", "_") + ".wiki"
                    filepath = os.path.join(f"{output_dir}/wiki_docs", filename)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    wiki_files_generated.append({
                        "name": page_name,
                        "title": title,
                        "filename": filename,
                        "content_length": len(content),
                        "layer": 1,
                        "status": "full_content"
                    })
                    
                    print(f"[Generated] {filename} (Layer 1)")
        
        elif api_type == "categorymembers":
            members = raw_data[key_name]["query"].get("categorymembers", [])
            
            sub_content = f"<!-- Category: {entry['params'].get('cmtitle', '')} -->\n"
            sub_content += f"<!-- This page contains {len(members)} sub-pages -->\n"
            sub_content += "<!-- Sub-pages list: -->\n"
            
            sub_titles = []
            for member in members:
                title = member.get("title", "Unknown")
                ns = member.get("ns", 0)
                
                if ns == 14:
                    continue
                
                sub_titles.append(title)
                sub_content += f"<!-- - {title} (pageid: {member.get('pageid', 'N/A')}) -->\n"
            
            filename = page_name.replace("/", "_") + ".wiki"
            filepath = os.path.join(f"{output_dir}/wiki_docs", filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(sub_content)
            
            wiki_files_generated.append({
                "name": page_name,
                "title": page_name,
                "filename": filename,
                "content_length": len(sub_content),
                "layer": 1,
                "status": "category_list",
                "sub_titles": sub_titles
            })
            
            print(f"[Generated] {filename} (Layer 1 - Category list with {len(sub_titles)} sub-pages)")
    
    print(f"\n=== Generated {len(wiki_files_generated)} wiki files ===")
    
    return wiki_files_generated

def analyze_raw_data():
    config = load_config()
    output_dir = config["output_dir"]
    
    raw_file = f"{output_dir}/l1_raw.json"
    
    if not os.path.exists(raw_file):
        print(f"[Error] Raw file not found: {raw_file}")
        return None
    
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    analysis = {
        "summary": {
            "total_pages": 8,
            "layer1_pages": 8,
            "layer2_pages": 0
        },
        "pages": [],
        "wiki_files": []
    }
    
    for entry in config["entry_pages"]:
        page_name = entry["name"]
        api_type = entry["api_type"]
        key_name = page_name.replace("/", "_")
        
        if key_name not in raw_data:
            continue
        
        if api_type == "revisions":
            pages = raw_data[key_name]["query"].get("pages", {})
            
            for pageid, pageinfo in pages.items():
                if "missing" in pageinfo:
                    continue
                
                title = pageinfo.get("title", "Unknown")
                revisions = pageinfo.get("revisions", [])
                
                if revisions:
                    content = revisions[0].get("*", "")
                    content_length = len(content)
                    filename = title.replace("/", "_").replace(" ", "_") + ".wiki"
                    
                    analysis["pages"].append({
                        "name": page_name,
                        "title": title,
                        "pageid": pageid,
                        "layer": 1,
                        "status": "full_content",
                        "content_length": content_length
                    })
                    
                    analysis["wiki_files"].append({
                        "name": page_name,
                        "title": title,
                        "filename": filename,
                        "content_length": content_length,
                        "layer": 1,
                        "status": "full_content"
                    })
        
        elif api_type == "categorymembers":
            members = raw_data[key_name]["query"].get("categorymembers", [])
            sub_titles = []
            
            for member in members:
                title = member.get("title", "Unknown")
                ns = member.get("ns", 0)
                
                if ns == 14:
                    continue
                
                sub_titles.append(title)
            
            filename = page_name.replace("/", "_") + ".wiki"
            
            analysis["pages"].append({
                "name": page_name,
                "title": page_name,
                "pageid": "",
                "layer": 1,
                "status": "category_list",
                "sub_titles": sub_titles,
                "sub_count": len(sub_titles)
            })
            
            analysis["wiki_files"].append({
                "name": page_name,
                "title": page_name,
                "filename": filename,
                "content_length": len(f"<!-- Category: {entry['params'].get('cmtitle', '')} -->\n<!-- This page contains {len(sub_titles)} sub-pages -->\n<!-- Sub-pages list: -->\n" + "\n".join([f"<!-- - {t} -->" for t in sub_titles])),
                "layer": 1,
                "status": "category_list",
                "sub_titles": sub_titles,
                "sub_count": len(sub_titles)
            })
    
    analysis_file = f"{output_dir}/l1_analysis.json"
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"[Saved] Analysis to {analysis_file}")
    
    print("\n=== Analysis Summary ===")
    print(f"Total Layer 1 pages: {analysis['summary']['layer1_pages']}")
    
    for page in analysis["pages"]:
        sub_info = f" ({page.get('sub_count', 0)} sub-pages)" if page.get("sub_titles") else ""
        print(f"  - {page['name']} ({page['status']}){sub_info}")
    
    return analysis

def main():
    print("=== Analyzing raw data ===")
    analyze_raw_data()
    
    print("\n=== Parsing raw data to wiki files ===")
    parse_raw_to_wiki()
    
    print("\n=== Done ===")

if __name__ == "__main__":
    main()