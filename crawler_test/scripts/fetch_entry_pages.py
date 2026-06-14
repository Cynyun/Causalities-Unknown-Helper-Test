import asyncio
import aiohttp
import json
import os
import re

BASE_URL = "https://scavprototype.wiki.gg/api.php"

# 要获取的入口页面列表
ENTRY_PAGES = [
    "Items",
    "Buildings",
    "Layers",
    "Lore",
    "Tiles",
    "Soundtrack",
    "Liquids",
    "Moodles"
]

async def fetch_page_content(session, titles, follow_redirects=True):
    """获取页面内容，支持自动跟随重定向"""
    params = {
        "action": "query",
        "titles": "|".join(titles),
        "prop": "revisions",
        "rvprop": "content",
        "format": "json"
    }
    
    # 添加重定向跟随参数
    if follow_redirects:
        params["redirects"] = "1"
    
    print(f"[Fetching] {len(titles)} pages: {titles}")
    
    async with session.get(BASE_URL, params=params) as response:
        if response.status != 200:
            print(f"[Error] HTTP status: {response.status}")
            return None, {}
        
        data = await response.json()
        return data, data.get("query", {}).get("redirects", [])

def is_redirect_page(pageinfo):
    """检查页面是否为重定向页面"""
    revisions = pageinfo.get("revisions", [])
    if not revisions:
        return False
    content = revisions[0].get("*", "")
    return content.strip().startswith("#REDIRECT")

def extract_redirect_target(content):
    """从重定向内容中提取目标页面"""
    content = content.strip()
    if content.startswith("#REDIRECT"):
        # 格式: #REDIRECT [[Page Name]]
        match = re.search(r'#REDIRECT\s*\[\[([^\]]+)\]\]', content, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

async def main():
    os.makedirs("output", exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        # 尝试获取所有入口页面（带重定向跟随）
        data, redirects_list = await fetch_page_content(session, ENTRY_PAGES, follow_redirects=True)
        
        if not data:
            print("[Error] Failed to fetch entry pages")
            return
        
        all_pages_data = data["query"].get("pages", {})
        
        # 显示所有页面的标题
        print(f"\n[Debug] All pages in response ({len(all_pages_data)} pages):")
        for pageid, pageinfo in all_pages_data.items():
            title = pageinfo.get("title", "")
            revisions = pageinfo.get("revisions", [])
            content = revisions[0].get("*", "") if revisions else ""
            is_redirect = content.strip().startswith("#REDIRECT")
            print(f"  - {title} (pageid: {pageid}, is_redirect: {is_redirect})")
        
        # 显示重定向信息
        if redirects_list:
            print(f"\n[Redirects] Auto-followed {len(redirects_list)} redirects:")
            for r in redirects_list:
                print(f"  {r['from']} -> {r['to']}")
        
        # 处理重定向：移除原始重定向页面，保留目标页面
        redirect_targets = set(r['to'] for r in redirects_list)
        print(f"\n[Debug] Redirect targets: {redirect_targets}")
        
        # 收集需要删除的页面ID
        pages_to_remove = []
        for pageid, pageinfo in all_pages_data.items():
            title = pageinfo.get("title", "")
            revisions = pageinfo.get("revisions", [])
            
            if revisions:
                content = revisions[0].get("*", "")
                is_redirect = content.strip().startswith("#REDIRECT")
                
                # 如果是原始的重定向页面（不在目标列表中），标记删除
                if is_redirect:
                    is_target = any(r['to'] == title for r in redirects_list)
                    if not is_target:
                        target = extract_redirect_target(content)
                        print(f"[Redirect] {title} -> {target} (will be removed)")
                        pages_to_remove.append(pageid)
        
        print(f"\n[Debug] Pages to remove: {pages_to_remove}")
        
        # 删除重定向页面
        for pageid in pages_to_remove:
            if pageid in all_pages_data:
                del all_pages_data[pageid]
                print(f"[Removed] pageid: {pageid}")
        
        print(f"\n[Debug] Remaining pages: {len(all_pages_data)}")
        
        # 构建输出数据
        output = {
            "batchcomplete": "",
            "query": {
                "pages": all_pages_data
            }
        }
        
        # 保存原始数据
        raw_file = "output/entry_pages_raw.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n[Saved] Raw data to {raw_file}")
        
        # 生成分析数据
        analysis = []
        for pageid, pageinfo in all_pages_data.items():
            title = pageinfo.get("title", "Unknown")
            ns = pageinfo.get("ns", 0)
            
            if "missing" in pageinfo:
                analysis.append({
                    "pageid": pageid,
                    "title": title,
                    "status": "missing",
                    "ns": ns
                })
                print(f"[Missing] {title}")
            else:
                revisions = pageinfo.get("revisions", [])
                if revisions:
                    content = revisions[0].get("*", "")
                    analysis.append({
                        "pageid": pageid,
                        "title": title,
                        "ns": ns,
                        "content_length": len(content),
                        "has_content": len(content) > 0,
                        "status": "success"
                    })
                    print(f"[OK] {title} ({len(content)} chars)")
                else:
                    analysis.append({
                        "pageid": pageid,
                        "title": title,
                        "ns": ns,
                        "status": "no_revisions"
                    })
        
        analysis_file = "output/entry_pages_analysis.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"\n[Saved] Analysis to {analysis_file}")
        
        # 保存页面到单独文件
        os.makedirs("output/entry_pages", exist_ok=True)
        
        # 删除旧的 wiki 文件
        print(f"\n[Debug] Deleting old files...")
        for filename in os.listdir("output/entry_pages"):
            if filename.endswith(".wiki") or filename.endswith(".txt"):
                filepath = os.path.join("output/entry_pages", filename)
                os.remove(filepath)
                print(f"[Deleted] {filename}")
        
        # 保存新页面
        print(f"\n[Debug] Saving new files...")
        for pageid, pageinfo in all_pages_data.items():
            if "missing" not in pageinfo:
                title = pageinfo.get("title", "Unknown")
                revisions = pageinfo.get("revisions", [])
                if revisions:
                    content = revisions[0].get("*", "")
                    content_format = revisions[0].get("contentformat", "")
                    
                    if content_format == "text/x-wiki":
                        ext = ".wiki"
                    else:
                        ext = ".txt"
                    
                    filename = title.replace("/", "_").replace(" ", "_") + ext
                    filepath = os.path.join("output/entry_pages", filename)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    print(f"[Saved] {title} -> {filename}")

if __name__ == "__main__":
    asyncio.run(main())