"""使用 .env 中的配置验证免费模型，找到可用模型后停止。"""

from pathlib import Path

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError

from llm_client import HelloAgentsLLM


# 名称来自 AIHubMix 官方免费模型列表；实际可用性以请求结果为准。
MODEL_CANDIDATES = (
    "glm-4.7-flash-free",
    "coding-glm-4.6-free",
    "mimo-v2-flash-free",
)


def find_available_model():
    load_dotenv(Path(__file__).with_name(".env"))
    for model in MODEL_CANDIDATES:
        llm = HelloAgentsLLM(model=model, timeout=30)
        # 诊断时关闭重试，避免重复消耗调用额度。
        client = llm.client.with_options(max_retries=0)
        print(f"测试免费模型：{model}", flush=True)
        try:
            content = []
            with client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Reply with exactly OK."}],
                temperature=0,
                max_tokens=128,
                stream=True,
            ) as response:
                for chunk in response:
                    if chunk.choices:
                        content.append(chunk.choices[0].delta.content or "")
            answer = "".join(content).strip()
            if "accounts that have not been recharged can only try 10 times" in answer.lower():
                print("账号的 10 次免费试用额度已用完，切换免费模型也无法解决。")
                print("可在 AIHubMix 控制台充值以开通免费模型每日额度，或配置其他可用服务。")
                return None
            if answer.upper().rstrip(".!。！") == "OK":
                print(f"可用模型：{model}")
                return model
            print(f"未返回预期的 OK，模型回复：{answer[:300]!r}")
        except APIStatusError as error:
            print(f"调用失败：HTTP {error.status_code}，错误码 {error.code}")
            if error.status_code in (401, 403, 429):
                print("请先检查 API Key、账号权限或调用额度。")
                return None
        except APIConnectionError:
            print("连接失败，请检查网络和 LLM_BASE_URL。")
            return None
        finally:
            client.close()
            llm.client.close()
    return None


if __name__ == "__main__":
    model = find_available_model()
    if model:
        print(f"可在 .env 中设置 LLM_MODEL_ID={model}")
    else:
        print("未找到已验证可用的免费模型。")
        raise SystemExit(1)
