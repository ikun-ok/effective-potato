import os
from github import Github
from openai import OpenAI

# --- 初始化 ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER")

g = Github(GITHUB_TOKEN)

issue = repo.get_issue(number=int(ISSUE_NUMBER))
client = OpenAI(api_key=OPENAI_API_KEY)

# --- 关键：同时读取Issue正文和所有评论里的图片 ---
def get_image_url():
    # 1. 先读Issue正文
    body = issue.body or ""
    lines = body.splitlines()
    for line in lines:
        if "![](" in line:
            return line.split("![](")[1].split(")")[0].strip()
        if line.startswith("http") and any(ext in line for ext in [".png", ".jpg", ".jpeg", ".webp"]):
            return line.strip()

    # 2. 再读所有评论
    comments = list(issue.get_comments())
    for comment in comments:
        c_body = comment.body or ""
        c_lines = c_body.splitlines()
        for line in c_lines:
            if "![](" in line:
                return line.split("![](")[1].split(")")[0].strip()
            if line.startswith("http") and any(ext in line for ext in [".png", ".jpg", ".jpeg", ".webp"]):
                return line.strip()
    return None

# --- 调用模型分析 ---
def analyze_dish(image_url):
    prompt = """
    你是专业的美食营养分析师。根据图片中的菜品，按以下格式输出信息：
    1. 菜名 & 菜系：（例如：番茄炒蛋，家常菜）
    2. 主要食材：（列出核心食材，如鸡蛋、番茄、食用油）
    3. 估算重量：（给出整道菜的大致重量，如约250g）
    4. 营养估算（基于食材常见做法）：
       - 热量：XXX kcal/整份
       - 蛋白质：XX g
       - 碳水化合物：XX g
       - 脂肪：XX g
    5. 健康建议：（如少油/控糖/适合减脂等，1-2句话）

    注意：所有数据为估算值，用友好的中文回答，格式清晰，控制在400字以内。
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]}
        ],
        max_tokens=600
    )
    return response.choices[0].message.content

# --- 主流程 ---
if __name__ == "__main__":
    print("开始运行智能体...")
    image_url = get_image_url()

    if not image_url:
        issue.create_comment("❌ 未找到图片链接，请重新上传菜品图片！")
        exit()

    try:
        print(f"找到图片：{image_url}")
        result = analyze_dish(image_url)
        comment = f"✅ 识别 & 营养分析结果：\n\n{result}\n\n⚠️ 以上为估算值，仅供参考。"
        issue.create_comment(comment)
        print("运行完成！")
    except Exception as e:
        print(f"出错：{e}")
        issue.create_comment(f"❌ 运行失败：{str(e)[:200]}")
