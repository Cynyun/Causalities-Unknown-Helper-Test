import os
import re

def parse_wiki_tables(wikitext):
    """解析所有 Wiki 表格并替换为 HTML"""
    pattern = r'\{\|\s*(.*?)\|\}'
    
    def replace_table(match):
        content = match.group(1)
        
        # 先按 |- 分割行
        row_sections = content.split('|-')
        html = '<table class="wiki-table">'
        
        for section in row_sections:
            section = section.strip()
            if not section:
                continue
            
            # 将 section 按换行分割处理
            lines = section.split('\n')
            current_row_html = ''
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 跳过纯属性行（只有 class= 或 style=）
                if re.match(r'^\s*(class|style)=', line) and '!' not in line:
                    continue
                
                # 这是一行表格内容
                cells = re.split(r'\|\|', line)
                current_row_html += '<tr>'
                
                for cell in cells:
                    cell = cell.strip()
                    if not cell:
                        continue
                    
                    # 检查是否是表头
                    if cell.startswith('!'):
                        header_text = cell[1:].strip()
                        current_row_html += f'<th>{header_text}</th>'
                    else:
                        # 清理单元格开头的 |
                        cell = re.sub(r'^\|', '', cell).strip()
                        # 清理单元格中的图片链接
                        cell = re.sub(r'\[\[File:([^\|\]]+)\|link=([^\|\]]+)\|\d+px\s*\]\]', r'<img src="https://scavprototype.wiki.gg/images/thumb/\1/30px-\1" alt="\2" class="wiki-image">', cell)
                        cell = re.sub(r'\[\[File:([^\|\]]+)\|\d+px\s*\]\]', r'<img src="https://scavprototype.wiki.gg/images/thumb/\1/30px-\1" alt="\1" class="wiki-image">', cell)
                        # 清理 Wiki 链接
                        cell = re.sub(r'\[\[([^\|\]]+)\|([^\]]+)\]\]', r'<a href="#/\1" class="wiki-link">\2</a>', cell)
                        cell = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="#/\1" class="wiki-link">\1</a>', cell)
                        current_row_html += f'<td>{cell}</td>'
                
                current_row_html += '</tr>'
            
            html += current_row_html
        
        html += '</table>'
        return html
    
    return re.sub(pattern, replace_table, wikitext, flags=re.DOTALL)

def simple_wikitext_to_html(wikitext):
    """将简单的 Wikitext 转换为 HTML"""
    html = wikitext
    
    # 移除模板调用 {{...}}
    html = re.sub(r'\{\{[^\}]+\}\}', '', html)
    
    # 移除 tabber 标签及其内容
    html = re.sub(r'<tabber>.*?</tabber>', '', html, flags=re.DOTALL)
    
    # 先处理表格（因为表格中可能包含其他需要处理的元素）
    html = parse_wiki_tables(html)
    
    # 处理标题
    html = re.sub(r'====\s*(.+?)\s*====', r'<h4>\1</h4>', html)
    html = re.sub(r'===\s*(.+?)\s*===', r'<h3>\1</h3>', html)
    html = re.sub(r'==\s*(.+?)\s*==', r'<h2>\1</h2>', html)
    
    # 处理粗体和斜体
    html = re.sub(r"'''(.+?)'''", r'<strong>\1</strong>', html)
    html = re.sub(r"''(.+?)''", r'<em>\1</em>', html)
    
    # 处理图片链接 [[File:Name.png|link=Page|size]]
    html = re.sub(r'\[\[File:([^\|\]]+)\|link=([^\|\]]+)\|\d+px\s*\]\]', r'<img src="https://scavprototype.wiki.gg/images/thumb/\1/50px-\1" alt="\2" class="wiki-image">', html)
    html = re.sub(r'\[\[File:([^\|\]]+)\|link=([^\|\]]+)\]\]', r'<img src="https://scavprototype.wiki.gg/images/thumb/\1/50px-\1" alt="\2" class="wiki-image">', html)
    html = re.sub(r'\[\[File:([^\|\]]+)\|\d+px\s*\]\]', r'<img src="https://scavprototype.wiki.gg/images/thumb/\1/80px-\1" alt="\1" class="wiki-image">', html)
    html = re.sub(r'\[\[File:([^\|\]]+)\]\]', r'<img src="https://scavprototype.wiki.gg/images/thumb/\1/80px-\1" alt="\1" class="wiki-image">', html)
    
    # 处理 Wiki 链接 [[Page|Text]] 或 [[Page]]
    html = re.sub(r'\[\[([^\|\]]+)\|([^\]]+)\]\]', r'<a href="#/\1" class="wiki-link">\2</a>', html)
    html = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="#/\1" class="wiki-link">\1</a>', html)
    
    # 处理列表
    html = re.sub(r'^\* (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # 处理换行
    html = re.sub(r'\n', r'<br>', html)
    
    return html

def generate_html(wiki_content, title):
    """生成完整的 HTML 页面"""
    content = simple_wikitext_to_html(wiki_content)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Scav Prototype Wiki</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }}
        
        header {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        header h1 {{
            font-size: 2em;
            background: linear-gradient(90deg, #00d4ff, #7b2fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .content {{
            line-height: 1.8;
            color: #d0d0d0;
        }}
        
        h2 {{
            color: #00d4ff;
            margin: 20px 0 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid rgba(0, 212, 255, 0.3);
        }}
        
        h3 {{
            color: #7b2fff;
            margin: 18px 0 8px;
        }}
        
        h4 {{
            color: #a0a0a0;
            margin: 15px 0 5px;
        }}
        
        strong {{
            color: #fff;
        }}
        
        em {{
            color: #aaa;
            font-style: italic;
        }}
        
        .wiki-link {{
            color: #00d4ff;
            text-decoration: none;
            border-bottom: 1px dashed rgba(0, 212, 255, 0.5);
        }}
        
        .wiki-link:hover {{
            color: #7b2fff;
            border-bottom-color: #7b2fff;
        }}
        
        .wiki-image {{
            max-width: 50px;
            height: auto;
            border-radius: 4px;
            margin: 5px;
            vertical-align: middle;
        }}
        
        .wiki-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .wiki-table th, .wiki-table td {{
            padding: 10px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .wiki-table th {{
            background: rgba(0, 212, 255, 0.1);
            color: #00d4ff;
            font-weight: 600;
        }}
        
        .wiki-table tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        ul {{
            margin: 10px 0 10px 30px;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        @media (max-width: 600px) {{
            .container {{
                padding: 15px;
            }}
            
            .wiki-table th, .wiki-table td {{
                padding: 8px 10px;
                font-size: 0.9em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
        </header>
        <div class="content">
            {content}
        </div>
    </div>
</body>
</html>'''
    
    return html

def convert_all_wiki_files(input_dir, output_dir):
    """转换所有 wiki 文件为 HTML"""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.wiki') and filename != 'Tiles.wiki':
            wiki_path = os.path.join(input_dir, filename)
            html_filename = filename.replace('.wiki', '.html')
            html_path = os.path.join(output_dir, html_filename)
            
            with open(wiki_path, 'r', encoding='utf-8') as f:
                wiki_content = f.read()
            
            title = filename.replace('.wiki', '').replace('_', ' ')
            html = generate_html(wiki_content, title)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"Generated: {html_filename}")

if __name__ == '__main__':
    input_dir = 'output/entry_pages'
    output_dir = 'output/entry_pages'
    convert_all_wiki_files(input_dir, output_dir)
    print("\nAll HTML files generated successfully!")