import requests

QWEN_KEY = "sk-9e13e1949f1f4ce1a957837ac0c539bc"

# 临时简易识别：不用图片，固定鸡蛋测试，先验证密钥连通
def analyze_dish_simple():
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = """识别鸡蛋，严格三行：
菜名：水煮鸡蛋
食材：鸡蛋
热量：143 kcal
"""
    req_data = {"model":"qwen3.7-plus","messages":[{"role":"user","content":prompt}]}
    resp = requests.post(url,headers=headers,json=req_data)
    json_res = resp.json()
    # 打印返回全部内容，看报错
    print(json_res)
    if "output" not in json_res:
        return f"错误:{json_res}"
    return json_res["output"]["text"]

# 页面调用
def food_agent_run(img_file):
    txt = analyze_dish_simple()
    if "错误:" in txt:
        return {"name":"调用失败","material":txt,"cal":"0"}
    name = txt.split("菜名：")[1].split("\n")[0].strip()
    material = txt.split("食材：")[1].split("\n")[0].strip()
    cal = txt.split("热量：")[1].replace("kcal","").strip()
    return {"name": name, "material": material, "cal": cal}

# 健康问答
def health_chat_answer(question):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    req_data = {"model":"qwen3.7-plus","messages":[{"role":"user","content":question}]}
    resp = requests.post(url,headers=headers,json=req_data)
    json_res = resp.json()
    if "output" not in json_res:
        return str(json_res)
    return json_res["output"]["text"]
