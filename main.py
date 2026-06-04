import base64
import requests

QWEN_KEY = "sk-9e13e1949f1f4ce1a957837ac0c539bc"

def analyze_dish(img_base64):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = """
你是专业美食营养师，识别图片菜品，严格只按如下三行格式输出，不要多余文字：
菜名：XXX
食材：XXX
热量：数字 kcal
"""
    data = {
        "model": "qwen-plus-latest",
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
    res = requests.post(url, headers=headers, json=data)
    json_data = res.json()
    result_text = json_data["output"]["choices"][0]["message"]["content"][0]["text"]
    return result_text

def food_agent_run(img_file):
    img_bytes = img_file.read()
    b64_code = base64.b64encode(img_bytes).decode()
    res_str = analyze_dish(b64_code)
    dish_name = res_str.split("菜名：")[1].split("\n")[0].strip()
    material = res_str.split("食材：")[1].split("\n")[0].strip()
    cal_num = res_str.split("热量：")[1].replace("kcal", "").strip()
    return {"name": dish_name,"material": material,"cal": cal_num}

def health_chat_answer(question):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"""你是私人健康营养师，简短回答饮食、运动、睡眠、减脂相关问题。用户：{question}"""
    data = {"model": "qwen3.7-plus","messages": [{"role": "user", "content": prompt}]}
    res = requests.post(url, headers=headers, json=data)
    json_data = res.json()
    return json_data["output"]["text"]
