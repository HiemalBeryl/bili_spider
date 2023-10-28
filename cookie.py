cookies = {
    "buvid3": "F0421EF5-2FDE-7D65-D650-2C9400BF8CC316452infoc",
    "b_nut": "1698222616",
    "CURRENT_FNVAL": "4048",
    "b_lsid": "CA10B7E107_18B65F4B84A",
    "_uuid": "104CEB109D-3241-7B107-109F2-2BF5D5A59C5918709infoc",
    "buvid_fp": "1802e0a5af37a17b2a1586943b24eaf2",
    "buvid4": "8CCE389D-A79A-1D2F-C371-B16B0E65F46218188-023102516-vHi6lkY+gC/JcV1zC0w1Ag%3D%3D",
    "rpdid": "|(k|YulRu~Ym0J'uYm)kkkYu)",
    "bili_ticket": "eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9"
                   ".eyJleHAiOjE2OTg0ODE4MjEsImlhdCI6MTY5ODIyMjU2MSwicGx0IjotMX0"
                   ".xt6g0MhUeqo_xbmLATkpUxDHnTQDuptyCnlyKBz9CnA",
    "bili_ticket_expires": "1698481761",
    "SESSDATA": "af581ed9%2C1713774826%2C1bd9b%2Aa1CjBgA_PT4DQA_7gDz6W9Gd2wN6aPZM9Br5TvRpoq_-zhhFHsV4QzPibzQl9Aj9"
                "-MD1wSVlNnTWZhM0pRU0p0SnNMY1IzQkRnT1VhQVQwRW1Mb3pQeGg2YTZBU1VsTjU1RjBoRmoyQlpKUGZ1OEt6T3R4MzBDeVN"
                "VZ0x4czcwTmpJbV8wQ3FXN253IIEC",
    "bili_jct": "97f7b5a187b27b160efcd69c7d14f2e7",
    "DedeUserID": "1829480924",
    "DedeUserID__ckMd5": "f3a5bbc575b2521f",
    "sid": "qcdzbunn",
    "PVID": "1"
}
result = []
for k, v in cookies.items():
    template = {'name': k, 'value': v, 'path': '/', 'domain': 'www.bilibili.com', 'secure': False, 'httpOnly': False}
    result.append(template)
print(result)