import os
from github import Github
from openai import OpenAI

# --- 初始化环境变量 ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER")

# 初始化客户端
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(number=int(ISSUE_NUMBER))
client = OpenAI(api_key=OPENAI_API_KEY)

# --- 步骤1：从Issue或评论中提取图片URL ---
def get_image_url(issue_body, comments):
    # 先检查Issue主体
    lines = issue_body.split("\n")
    for line in lines:
        if "![](" in line:
            return line.split("![](")[1].split(")")[0]
        if line.startswith("http") and any(ext in line for ext in [".png", ".jpg", ".jpeg", ".webp"]):
            return line
    # 再检查所有评论
    for comment in comments:
        body = comment.body or ""
        lines = body.split("\n")
        for line in lines:
            if "![](" in line:
                return line.split("![](")[1].split(")")[0]
            if line.startswith("http") and any(ext in line for ext in [".png", ".jpg", ".jpeg", ".webp"]):
                return line
    return None

# --- 步骤2：调用GPT-4o识别菜品并分析热量 ---
def analyze_dish_with_nutrition(image_url):
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
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=600
    )
    return response.choices[0].message.content

# --- 主流程 ---
if __name__ == "__main__":
    print("收到新Issue/评论，开始处理...")
    # 收集Issue主体和所有评论
    issue_body = issue.body or ""
    comments = list(issue.get_comments())
    image_url = get_image_url(issue_body, comments)

    if not image_url:
        issue.create_comment("❌ 未在Issue或评论中找到图片，请重新上传菜品图片~")
        exit()

    try:
        print(f"正在识别并分析营养：{image_url}")
        result = analyze_dish_with_nutrition(image_url)
        comment_body = f"✅ 识别 & 营养分析结果如下：\n\n{result}\n\n⚠️ 以上热量和营养数据为估算值，仅供参考。"
        issue.create_comment(comment_body)
        print("处理完成，已回复Issue！")
    except Exception as e:
        print(f"出错了：{e}")
        issue.create_comment(f"❌ 识别失败了，错误信息：{str(e)[:200]}")
