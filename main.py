import base64
import requests
import streamlit as st

def get_qwen_key():
    return st.secrets["QWEN_KEY"]

# 菜品识图分析
def analyze_dish(img_base64):
    api_key = get_qwen_key()
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = """
你是专业美食营养师，识别图片菜品，严格只按如下三行格式输出，不要多余文字：
菜名：XXX
食材：XXX
热量：数字 kcal
"""
    data = {
        "model": "qwen-vl-plus",
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
    result_text = res.json()["output"]["choices"][0]["message"]["content"][0]["text"]
    return result_text

# 网页上传图片调用入口
def food_agent_run(img_file):
    img_bytes = img_file.read()
    b64_code = base64.b64encode(img_bytes).decode()
    res_str = analyze_dish(b64_code)
    dish_name = res_str.split("菜名：")[1].split("\n")[0].strip()
    material = res_str.split("食材：")[1].split("\n")[0].strip()
    cal_num = res_str.split("热量：")[1].replace("kcal", "").strip()
    return {
        "name": dish_name,
        "material": material,
        "cal": cal_num
    }

# AI健康问答
def health_chat_answer(question):
    api_key = get_qwen_key()
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"""你是私人健康营养师，简短回答饮食、运动、睡眠、减脂相关问题。
用户提问：{question}
"""
    data = {
        "model": "qwen-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()["output"]["text"]
