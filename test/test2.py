import httpx





if __name__ == "__main__":
    url = "https://api.example.com/endpoint"  # 请替换为实际的 API 地址
    params = {'param1': 'value1', 'param2': 'value2'}
    headers = {'User-Agent': 'MyClient'}

    data = fetch_data(url, method='GET', params=params, headers=headers)

    if data:
        print(data)
