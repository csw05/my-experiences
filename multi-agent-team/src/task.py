"""代码审查任务模板"""

# 内置示例代码（用于演示或终端默认审查对象）
SAMPLE_CODE = '''def calculate_total(items):
    total = 0
    for item in items:
        total += item["price"]
    return total


def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return database.execute(query)


def process_order(order):
    if order["status"] == "new":
        send_email(order["email"], "订单已确认")
        order["status"] = "confirmed"
    elif order["status"] == "confirmed":
        ship_order(order)
        order["status"] = "shipped"
    return order
'''

SAMPLE_LANGUAGE = "python"


def build_task(code: str, language: str = "") -> str:
    """根据用户提交的代码构建审查任务"""
    lang_hint = f"（语言：{language}）" if language else "（请自动识别语言）"
    lines = code.strip().count("\n") + 1

    return f"""请对以下代码进行全面的代码审查{lang_hint}：

```
{code}
```

审查说明：
- 以上代码共 {lines} 行，请各角色按职责依次审查，不要跳过任何角色
- 每个角色聚焦自己的专业领域，不越界
- 最终由用户代理汇总为结构化 Markdown 报告

请团队协作完成这次代码审查任务。"""
