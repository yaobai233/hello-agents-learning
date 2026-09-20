import requests
import time

# ========= 这里改你的信息 =========
API_KEY = "sk-uLrFEVqtJwqia1XD987f2346Cc9948Cb86Bd8f2"  # 填入你的 aihubmix api key
BASE_URL = "https://aihubmix.com/v1/chat/completions"

# 候选免费模型列表，可以自行增删
model_list = [
    "deepseek-v3-free",
    "qwen2.5-7b-free",
    "glm-4-flash-free",
    "llama3.1-8b-free"
]
# ==================================

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

test_msg = {
    "model": "",
    "messages": [{"role": "user", "content": "你好，简单回答我一句话"}],
    "temperature": 0.3
}

def test_model(model_name):
    test_msg["model"] = model_name
    try:
        resp = requests.post(BASE_URL, headers=headers, json=test_msg, timeout=30)
        res_json = resp.json()
        if resp.status_code == 200:
            ans = res_json["choices"][0]["message"]["content"]
            print(f"✅【可用】{model_name}，返回内容：{ans}")
            return True, model_name
        else:
            err_msg = res_json.get("error", {}).get("message", "未知错误")
            print(f"❌【不可用】{model_name} | status:{resp.status_code} | {err_msg}")
            return False, model_name
    except Exception as e:
        print(f"⚠️【异常】{model_name} | {str(e)}")
        return False, model_name


if __name__ == "__main__":
    print("开始逐个测试免费模型...\n")
    available_model = None
    for m in model_list:
        ok, name = test_model(m)
        if ok:
            available_model = name
            break
        time.sleep(1.2)  # 间隔，防止429限流
    if available_model:
        print(f"\n🎉 找到可用模型：{available_model}")
        print("你可以把这个模型名字复制，放到你原来LLM调用代码的model变量中使用")
    else:
        print("\n❌ 当前所有测试模型都不可用，稍后再试")
