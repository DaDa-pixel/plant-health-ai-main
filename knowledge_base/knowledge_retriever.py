# knowledge_base/knowledge_retriever.py
import json
import os
from pathlib import Path


class KnowledgeRetriever:
    """本地知识库检索器 - 纯查询，无外部依赖"""

    def __init__(self, knowledge_file=None):
        if knowledge_file is None:
            knowledge_file = Path(__file__).parent / "disease_knowledge_formatted.json"

        self.knowledge = self._load_knowledge(knowledge_file)

    def _load_knowledge(self, file_path):
        """加载知识库"""
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_advice(self, disease_name):
        """
        从知识库检索病害信息
        返回: (found, advice_text, details)
        """
        # 精确匹配
        if disease_name in self.knowledge:
            info = self.knowledge[disease_name]
            advice = self._format_advice(info)
            return True, advice, info

        # 模糊匹配
        for key in self.knowledge:
            if key in disease_name or disease_name in key:
                info = self.knowledge[key]
                advice = self._format_advice(info, is_fuzzy=True, matched_key=key)
                return True, advice, info

        return False, None, None

    def _format_advice(self, info, is_fuzzy=False, matched_key=None):
        """格式化知识库输出"""
        if is_fuzzy:
            header = f"📚【知识库参考】找到相似病害「{matched_key}」的信息：\n\n"
        else:
            header = "📚【权威知识库】防治建议（来源：CropDP-KG/安徽农网）：\n\n"

        advice = header
        advice += f"🌱 症状：{info.get('symptoms', '暂无')}\n\n"
        advice += f"🌾 病因/发病规律：{info.get('cause', '暂无')}\n\n"
        advice += f"🧑‍🌾 农业防治：{info.get('prevention', '注意田间管理，合理轮作')}\n\n"

        treatment = info.get('treatment', '暂无')
        chemicals = info.get('chemicals', [])
        if chemicals:
            treatment += f"\n\n推荐药剂：{', '.join(chemicals)}"

        advice += f"💊 化学防治：{treatment}\n"
        advice += "\n💡 温馨提示：本建议仅供参考，请结合实际情况使用。"

        return advice

    def get_raw_info(self, disease_name):
        """获取原始知识库信息（供API调用）"""
        if disease_name in self.knowledge:
            return self.knowledge[disease_name]
        for key in self.knowledge:
            if key in disease_name or disease_name in key:
                return self.knowledge[key]
        return None

    def has_knowledge(self, disease_name):
        """检查是否有该病害的知识"""
        return disease_name in self.knowledge


# 测试代码
if __name__ == "__main__":
    retriever = KnowledgeRetriever()
    found, advice, _ = retriever.get_advice("番茄早疫病")
    if found:
        print(advice)