import base64
import requests

QWEN_KEY = "sk-9e13e1949f1f4ce1a957837ac0c539bc"

def analyze_dish(img_bytes):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    b64 = base64.b64encode(img_bytes).decode()
    # 通义最简prompt拼接图片，放弃messages结构（报错根源）
    prompt = f"""
图片：{b64}
你是专业美食营养师，识别图片菜品，严格只输出三行：
菜名：XXX
食材：XXX
热量：数字 kcal
"""
    payload = {
        "model": "qwen-vl",
        "prompt": prompt
    }
    res = requests.post(url, headers=headers, json=payload)
    json_res = res.json()
    if "output" not in json_res:
        return str(json_res)
    return json_res["output"]["choices"][0]["message"]["content"]

def food_agent_run(img_file):
    img_bytes = img_file.read()
    res_str = analyze_dish(img_bytes)
    if "code" in res_str:
        return {"name":"调用失败","material":res_str,"cal":"0"}
    name = res_str.split("菜名：")[1].split("\n")[0].strip()
    material = res_str.split("食材：")[1].split("\n")[0].strip()
    cal = res_str.split("热量：")[1].replace("kcal","").strip()
    return {"name":name,"material":material,"cal":cal}

# 文本问答
def health_chat_answer(question):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {"Authorization":f"Bearer {api_key}","Content-Type":"application/json"}
    payload = {"model":"qwen3.7-plus","prompt":question}
    res = requests.post(url,headers=headers,json=payload)
    json_res = res.json()
    if "output" not in json_res:
        return str(json_res)
    return json_res["output"]["text"]
