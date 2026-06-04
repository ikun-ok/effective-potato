import base64
import streamlit as st
from openai import OpenAI

# 读取密钥（从streamlit后台Secrets，不硬编码密钥）
def get_agent_client():
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
    return client

# 菜品图片识别、算热量
def analyze_dish(img_base64):
    client = get_agent_client()
    prompt = """
你是资深营养师，识别图片菜品，严格按下面格式返回：
菜名：xxx
食材：xxx
热量：数字 kcal
"""
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            }
        ]
    )
    return res.choices[0].message.content

# streamlit页面调用入口
def food_agent_run(img_file):
    img_bytes = img_file.read()
    b64 = base64.b64encode(img_bytes).decode()
    text = analyze_dish(b64)

    # 拆分结果
    name = text.split("菜名：")[1].split("\n")[0].strip()
    material = text.split("食材：")[1].split("\n")[0].strip()
    cal = text.split("热量：")[1].replace("kcal","").strip()

    return {
        "name": name,
        "material": material,
        "cal": cal
    }

# AI健康问答（健康页面专用）
def health_chat_answer(question):
    client = get_agent_client()
    prompt = f"""你是私人健康营养师，简洁回答用户饮食、运动、睡眠问题。
用户问题：{question}
"""
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content
