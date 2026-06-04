import os
from openai import OpenAI

# 只保留大模型密钥，从Streamlit Secrets读取
def get_agent_client():
    api_key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)

# 解析图片菜品信息
def analyze_dish(image_url):
    client = get_agent_client()
    prompt = """你是专业的美食营养师。根据图片中的菜品，按以下格式输出信息：
1. 菜名 & 菜系：（例如：番茄炒蛋，家常菜）
2. 主要食材：（列出核心食材，如鸡蛋、番茄、食用油）
3. 估算重量：（给出整道菜的大致重量，如约250g）
4. 营养估算（基于食材常见做法）：
- 热量：xxx kcal/整份"""
    resp = client.chat.completions.create(
        model="gpt-4v",
        messages=[{"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":image_url}}]}]
    )
    return resp.choices[0].message.content

# 给Streamlit调用的入口函数（网页上传图片后调用）
def food_agent_run(img_file):
    # 网页上传的本地图片转临时url/base64，这里简化适配
    import base64
    img_bytes = img_file.read()
    base64_str = base64.b64encode(img_bytes).decode()
    img_url = f"data:image/png;base64,{base64_str}"
    res_text = analyze_dish(img_url)
    # 拆分结果成字典方便网页展示
    return {
        "name":res_text.split("菜名 & 菜系：")[1].split("\n")[0],
        "material":res_text.split("主要食材：")[1].split("\n")[0],
        "cal":res_text.split("热量：")[1].split("kcal")[0].strip()
    }
