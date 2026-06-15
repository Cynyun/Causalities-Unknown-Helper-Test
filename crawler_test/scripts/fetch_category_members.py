import asyncio
import aiohttp
import json
import os
from typing import List, Dict, Any

BASE_URL = "https://scavprototype.wiki.gg/api.php"

async def fetch_category_members(session: aiohttp.ClientSession, category: str) -> List[Dict[str, Any]]:
    """
    Fetch category members from the wiki API
    
    Args:
        session: aiohttp session
        category: Category name (e.g., "Category:Mechanics")
    
    Returns:
        List of category member entries
    """
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmtype": "subcat|page",
        "cmlimit": 500,
        "format": "json"
    }
    
    print(f"Fetching category: {category}")
    print(f"Params: {params}")
    
    all_members = []
    continue_params = {}
    
    try:
        while True:
            request_params = {**params, **continue_params}
            
            async with session.get(BASE_URL, params=request_params) as response:
                if response.status != 200:
                    print(f"Request failed with status: {response.status}")
                    break
                
                data = await response.json()
                
                if "query" in data and "categorymembers" in data["query"]:
                    members = data["query"]["categorymembers"]
                    all_members.extend(members)
                    print(f"Fetched {len(members)} members, total: {len(all_members)}")
                
                # Check for continuation
                if "continue" in data:
                    continue_params = data["continue"]
                else:
                    break
                    
                # Rate limiting
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"Error fetching category members: {e}")
    
    return all_members

async def fetch_all_categories(categories: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch multiple categories"""
    async with aiohttp.ClientSession() as session:
        results = {}
        
        for category in categories:
            members = await fetch_category_members(session, category)
            results[category] = members
            await asyncio.sleep(2)  # Wait between categories
        
        return results

def save_results(results: Dict[str, List[Dict[str, Any]]], output_dir: str = "output/categories") -> None:
    """Save results to JSON files"""
    os.makedirs(output_dir, exist_ok=True)
    
    for category, members in results.items():
        # Clean category name for filename
        filename = category.replace("Category:", "").replace(" ", "_") + ".json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(members)} members to {filepath}")

def print_summary(results: Dict[str, List[Dict[str, Any]]]) -> None:
    """Print summary of results"""
    print("\n=== Summary ===")
    for category, members in results.items():
        print(f"{category}: {len(members)} pages")
        
        # Print first 5 page titles as preview
        if members:
            titles = [m["title"] for m in members[:5]]
            print(f"  First 5: {', '.join(titles)}")
            
            # Check for subcategories
            subcats = [m for m in members if m.get("ns") == 14]  # NS_CATEGORY = 14
            print(f"  Subcategories: {len(subcats)}")
            print(f"  Pages: {len(members) - len(subcats)}")

if __name__ == "__main__":
    # Category to fetch (only Category:Mechanics as specified)
    category_to_fetch = "Category:Mechanics"
    
    print("=== Category Members Crawler ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Category to fetch: {category_to_fetch}\n")
    
    # Run the crawler
    results = asyncio.run(fetch_all_categories([category_to_fetch]))
    
    # Save results
    save_results(results)
    
    # Print summary
    print_summary(results)