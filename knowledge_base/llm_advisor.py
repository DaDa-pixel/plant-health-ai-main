# knowledge_base/llm_advisor.py
import requests
import json
from pathlib import Path


class LLMAdvisor:
    """本地大模型咨询器 - 封装Ollama API调用"""

    def __init__(self, model_name="plantdoctor", ollama_url="http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        self.current_disease = None
        self._available = None  # 缓存可用性状态

    def set_disease_context(self, disease_name):
        """设置当前对话的病害上下文"""
        self.current_disease = disease_name

    def get_advice(self, disease_name):
        """
        获取病害的防治建议（首次咨询）
        """
        self.current_disease = disease_name
        prompt = f"""用户刚刚通过图像识别诊断出作物病害：「{disease_name}」。

请提供以下信息：
1. 该病害的典型症状
2. 发病条件（什么情况下容易发生）
3. 农业防治措施
4. 化学防治措施（推荐药剂和使用方法）

请用简洁、实用的语言回答，适合农民阅读。"""

        return self._call_llm(prompt)

    def chat(self, user_message):
        """
        多轮对话（基于当前病害上下文）
        """
        if not self.current_disease:
            return "请先上传叶片图片进行诊断，我会根据诊断结果为您提供专业建议。"

        prompt = f"""用户之前被诊断出患有「{self.current_disease}」，现在问：{user_message}

请以植物病理学专家的身份回答，用简洁实用的语言。"""

        return self._call_llm(prompt)

    def _call_llm(self, prompt):
        """调用 Ollama API"""
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.85,  # 提高温度，增加多样性
                        "top_p": 0.9,
                        "num_predict": 1024
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"AI服务暂时不可用 (错误码: {response.status_code})"

        except Exception as e:
            return f"AI服务错误: {e}"

    def is_available(self):
        """检查大模型是否可用（带缓存）"""
        if self._available is not None:
            return self._available

        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"].split(':')[0] for m in models]
                self._available = self.model_name.split(':')[0] in model_names
                return self._available
            self._available = False
            return False
        except:
            self._available = False
            return False

    def get_status_message(self):
        """获取状态信息（用于界面显示）"""
        if self.is_available():
            return f"✅ AI植保专家已就绪（模型：{self.model_name}）"
        else:
            return "⚠️ AI植保专家未连接，请运行 `ollama serve` 启动服务"


# 测试代码
if __name__ == "__main__":
    advisor = LLMAdvisor()
    ok = advisor.is_available()
    print(advisor.get_status_message())
    if ok:
        print("\n测试咨询：")
        result = advisor.get_advice("玉米大斑病")
        print(result[:300] + "...")