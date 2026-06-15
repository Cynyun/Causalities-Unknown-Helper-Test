**第一层入口页面（8个）：**

| 页面 | API 类型 | 参数 |
|------|---------|------|
| Items | revisions | `action=query, titles=Items, prop=revisions, rvprop=content, format=json` |
| Buildings | revisions | `action=query, titles=Buildings, prop=revisions, rvprop=content, format=json` |
| Layers | revisions | `action=query, titles=Layers, prop=revisions, rvprop=content, format=json` |
| Lore | revisions | `action=query, titles=Lore, prop=revisions, rvprop=content, format=json` |
| Tiles | revisions | `action=query, titles=Tiles, prop=revisions, rvprop=content, format=json` |
| Soundtrack | revisions | `action=query, titles=Soundtrack, prop=revisions, rvprop=content, format=json` |
| Liquids | revisions | `action=query, titles=Liquids, prop=revisions, rvprop=content, format=json` |
| Mechanics/Moodles | categorymembers | `action=query, list=categorymembers, cmtitle=Category:Mechanics, cmtype=subcat\|page, cmlimit=500, format=json` |