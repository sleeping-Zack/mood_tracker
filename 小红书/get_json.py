import requests

cookies = {
    'abRequestId': 'a75eea56-b395-578e-96b3-9b3fdedf06ac',
    'xsecappid': 'xhs-pc-web',
    'a1': '196af0ffde6f8o1c14286ebbyl700wybketm1idq150000188442',
    'webId': '0d0899283c49f267bda6e692793387a6',
    'gid': 'yjK0i8iiiYTqyjK0i8iifd3fdKiYlySy4JYK9AydDDv1W62888EvDy888yYY44J82dK2SqqS',
    'webBuild': '4.62.3',
    'acw_tc': '0ad6fbf917467594570006499e2a223bb7b9f7b73eccbc41d486261d125a46',
    'websectiga': 'cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c',
    'sec_poison_id': 'e6c49d20-4e35-468b-82ff-b05ca6b77818',
    'unread': '{%22ub%22:%2267fc24f9000000001c00c497%22%2C%22ue%22:%2267fdb17f000000001d02e680%22%2C%22uc%22:25}',
    'web_session': '0400698e8bad03579829fa27283a4b72e869a5',
    'loadts': '1746759597133',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.xiaohongshu.com',
    'priority': 'u=1, i',
    'referer': 'https://www.xiaohongshu.com/',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
    'x-b3-traceid': '1713465a53e8f539',
    'x-mns': 'unload',
    'x-s': 'XYW_eyJzaWduU3ZuIjoiNTYiLCJzaWduVHlwZSI6IngyIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6IjBlNzYwNGFhOGU5Y2NjM2NkNTkyYzExZWIxZjU3OWM2MTRjM2UzZWRhNDdhOTI2Mzk4ZGNkOTk1NmY5NjYwNjQzN2YxODUwYjFiZTQwYmE1Y2I4YjFiNDRlOTU1YjIzMjhhNDI4ZTcxZjZkNDQ2ZjJjOWY1NjE1NGU5NzE4MThlMWU1OTY4MGNjZWQzMGZhNWU0MjQ3ODQyY2EzOGQyMGJmMzYwYjExNjhjZGYwN2E2YmFjNTFhZjA4MjIzMzgwZTNlYzgxYTQ2NDE3NmI1ZWM3YmExNjE1Yjg5OWYzYjYxOTExMWQxYjUzNjNhYzJiZWE4OTFkZDUzNjRkYmVkNmRiN2E5Mzg0N2Y2M2FhOGU5N2RkZTg0NzVjN2RhMWM1NGY2NjEwMWI4YTA4YzFlMmI0NjRlMDRmNjFjMmJkYWVkY2RlZjlhMjMxMDQ1NjhmOGJiMzdlOTExMzUzZGYxN2E1NmE4ZjY0MzdmZTg3NTkwMjEzNDNkMmE2ODNhYjdlZjM5N2M4NjkxM2EyM2U3NDIxMTU0NTljNzhlYTE5YTFmIn0=',
    'x-s-common': '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',
    'x-t': '1746759597823',
    'x-xray-traceid': 'cb597e1eef34671abd8912536ce68c19',
    # 'cookie': 'abRequestId=a75eea56-b395-578e-96b3-9b3fdedf06ac; xsecappid=xhs-pc-web; a1=196af0ffde6f8o1c14286ebbyl700wybketm1idq150000188442; webId=0d0899283c49f267bda6e692793387a6; gid=yjK0i8iiiYTqyjK0i8iifd3fdKiYlySy4JYK9AydDDv1W62888EvDy888yYY44J82dK2SqqS; webBuild=4.62.3; acw_tc=0ad6fbf917467594570006499e2a223bb7b9f7b73eccbc41d486261d125a46; websectiga=cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c; sec_poison_id=e6c49d20-4e35-468b-82ff-b05ca6b77818; unread={%22ub%22:%2267fc24f9000000001c00c497%22%2C%22ue%22:%2267fdb17f000000001d02e680%22%2C%22uc%22:25}; web_session=0400698e8bad03579829fa27283a4b72e869a5; loadts=1746759597133',
}

json_data = {
    'keyword': '积极向上的文案',
    'page': 1,
    'page_size': 20,
    'search_id': '2erz6dbahavakk45bmwv4',
    'sort': 'general',
    'note_type': 0,
    'ext_flags': [],
    'geo': '',
    'image_formats': [
        'jpg',
        'webp',
        'avif',
    ],
}

response = requests.post(
    'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
    cookies=cookies,
    headers=headers,
    json=json_data,
)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
data = '{"keyword":"积极向上的文案","page":1,"page_size":20,"search_id":"2erz6dbahavakk45bmwv4","sort":"general","note_type":0,"ext_flags":[],"geo":"","image_formats":["jpg","webp","avif"]}'.encode()
response = requests.post('https://edith.xiaohongshu.com/api/sns/web/v1/search/notes', cookies=cookies, headers=headers, data=data)
print(response.text)