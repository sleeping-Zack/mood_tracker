import json

# 读取 xiaohongshu.json 文件内容
with open('xiaohongshu.json', 'r', encoding='utf-8') as file:
    # 直接解析 JSON
    parsed_data = json.load(file)

# 存放拼接好的链接
urls = []

# 遍历所有的 items
items = parsed_data["data"]["items"]
for item in items:
    _id = item["id"]
    xsec_token = item.get("xsec_token", None)

    # 如果外部没有找到 xsec_token，从 note_card 的 user 里找
    if not xsec_token and "note_card" in item:
        xsec_token = item["note_card"]["user"].get("xsec_token", "")

    # 拼接链接
    if _id and xsec_token:
        url = f"https://www.xiaohongshu.com/explore/{_id}?xsec_token={xsec_token}&xsec_source=pc_search&source=web_explore_feed"
        urls.append(url)

# 打印所有拼接好的链接
for link in urls:
    print(link)
