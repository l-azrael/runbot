import requests

YAPI_BASE_URL = "http://yapi.huacjian.cn"  # YApi 平台地址
API_TOKEN = "7bcd4f755562f91deeaf2859ba9a716db519f04271840eca21cbece405bf253c"  # 你的 API Token


def get_project_interfaces(cat_id):
    """
    根据分类获取接口详情
    """
    url = f"{YAPI_BASE_URL}/api/interface/list_cat"
    params = {
        "token": API_TOKEN,
        "catid": cat_id,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", {}).get("list", [])
    else:
        raise Exception(f"Failed to fetch interfaces: {response.text}")
