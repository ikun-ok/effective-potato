import base64
import requests

QWEN_KEY = "sk-9e13e1949f1f4ce1a957837ac0c539bc"

# 菜品识图（使用你账号自带的VL识图模型）
def analyze_dish(img_base64):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = """
你是专业美食营养师，识别图片菜品，严格只三行，无多余文字：
菜名：XXX
食材：XXX
热量：数字 kcal
"""
    req_data = {
        "model": "qwen3-vl-235b-a22b-thinking",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=req_data)
    json_res = resp.json()
    # 打印报错内容，方便查看
    print(json_res)
    content = json_res["output"]["choices"][0]["message"]["content"][0]["text"]
    return content

def food_agent_run(img_file):
    byte_data = img_file.read()
    b64_str = base64.b64encode(byte_data).decode()
    txt = analyze_dish(b64_str)
    name = txt.split("菜名：")[1].split("\n")[0].strip()
    material = txt.split("食材：")[1].split("\n")[0].strip()
    cal = txt.split("热量：")[1].replace("kcal", "").strip()
    return {"name": name, "material": material, "cal": cal}

# 健康问答
def health_chat_answer(question):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"营养师，简短回答健康问题：{question}"
    req_data = {
        "model": "qwen3.7-plus",
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post(url, headers=headers, json=req_data)
    json_res = resp.json()
    return json_res["output"]["text"]
