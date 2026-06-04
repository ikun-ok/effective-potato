import base64
import requests

QWEN_KEY = "sk-9e13e1949f1f4ce1a957837ac0c539bc"

def analyze_dish(img_bytes):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = """
你是专业美食营养师，识别图片菜品，严格只输出三行：
菜名：XXX
食材：XXX
热量：数字 kcal
"""
    # 修正：二进制base64不再拼装data:url，直接填入image字段
    b64_code = base64.b64encode(img_bytes).decode()
    req_data = {
        "model": "qwen3-vl-235b-a22b-thinking",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "image": b64_code
                    }
                ]
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=req_data)
    json_res = resp.json()
    if "output" not in json_res:
        return str(json_res)
    content = json_res["output"]["choices"][0]["message"]["content"][0]["text"]
    return content

def food_agent_run(img_file):
    img_bytes = img_file.read()
    res_str = analyze_dish(img_bytes)
    if "code" in res_str or "错误" in res_str:
        return {"name":"调用失败","material":res_str,"cal":"0"}
    name = res_str.split("菜名：")[1].split("\n")[0].strip()
    material = res_str.split("食材：")[1].split("\n")[0].strip()
    cal = res_str.split("热量：")[1].replace("kcal", "").strip()
    return {"name": name, "material": material, "cal": cal}

# AI健康问答
def health_chat_answer(question):
    api_key = QWEN_KEY
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"你是私人营养师，精简回答：{question}"
    req_data = {"model": "qwen3.7-plus", "messages": [{"role": "user", "content": prompt}]}
    resp = requests.post(url, headers=headers, json=req_data)
    json_res = resp.json()
    if "output" not in json_res:
        return str(json_res)
    return json_res["output"]["text"]
