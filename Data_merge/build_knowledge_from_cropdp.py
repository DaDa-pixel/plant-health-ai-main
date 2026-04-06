import os
import pandas as pd
import json
from pathlib import Path

# ==================== 配置路径 ====================
# 获取当前脚本所在目录（Data_merge 文件夹）
SCRIPT_DIR = Path(__file__).parent.absolute()
# 项目根目录（上级目录）
PROJECT_ROOT = SCRIPT_DIR.parent

# CropDP-KG 数据文件夹路径（在 datasets 下）
DATA_DIR = PROJECT_ROOT / "datasets" / "CropDP-KG-CropDP-KG-originData"

# 你的病害列表来源（从数据集文件夹读取）
DISEASE_FOLDER = PROJECT_ROOT / "datasets" / "raw" / "color"

# 知识库输出目录（在项目根目录下新建 knowledge_base 文件夹）
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"
KNOWLEDGE_DIR.mkdir(exist_ok=True)  # 如果文件夹不存在，自动创建

# 输出文件路径
OUTPUT_FILE = KNOWLEDGE_DIR / "disease_knowledge.json"
FORMATTED_FILE = KNOWLEDGE_DIR / "disease_knowledge_formatted.json"

# 中英文映射（从项目根目录导入）
import sys

sys.path.insert(0, str(PROJECT_ROOT))
try:
    from disease_names_cn import DISEASE_NAMES_CN
except ImportError:
    DISEASE_NAMES_CN = {}


# ==================== 以下函数保持不变 ====================
def get_your_diseases():
    """从数据集文件夹读取你的病害列表"""
    diseases = []
    if not DISEASE_FOLDER.exists():
        print(f"❌ 病害文件夹不存在: {DISEASE_FOLDER}")
        return []
    for folder in DISEASE_FOLDER.iterdir():
        if folder.is_dir():
            diseases.append(folder.name)
    return sorted(diseases)


def get_chinese_name(english_name):
    """将英文文件夹名转换为中文名"""
    if english_name in DISEASE_NAMES_CN:
        return DISEASE_NAMES_CN[english_name]
    return english_name.replace('_', ' ').replace('___', ' ')


def load_cropdp_data():
    """加载所有 Excel 文件，合并为一个 DataFrame"""
    all_data = []

    if not DATA_DIR.exists():
        print(f"❌ CropDP-KG 数据文件夹不存在: {DATA_DIR}")
        return None

    excel_files = sorted(DATA_DIR.glob("data*.xls"))

    if not excel_files:
        print(f"❌ 在 {DATA_DIR} 中没有找到 data*.xls 文件")
        return None

    print(f"找到 {len(excel_files)} 个数据文件:")
    for f in excel_files:
        print(f"  - {f.name}")

    for file in excel_files:
        try:
            df = pd.read_excel(file, engine='openpyxl')
            df = df.dropna(how='all')
            all_data.append(df)
            print(f"  ✓ 加载 {file.name}: {len(df)} 条记录")
        except Exception as e:
            print(f"  ✗ 加载失败 {file.name}: {e}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        first_col = combined.columns[0]
        combined = combined.drop_duplicates(subset=[first_col])
        print(f"\n总共加载 {len(combined)} 条病害记录（去重后）")
        return combined
    return None


def match_diseases(your_diseases, cropdp_df):
    """将你的病害与 CropDP-KG 数据匹配"""
    knowledge = {}

    col_names = list(cropdp_df.columns)
    print(f"\nCropDP-KG 数据列名: {col_names}")

    name_col = col_names[0]
    english_col = col_names[1] if len(col_names) > 1 else None
    symptom_col = col_names[3] if len(col_names) > 3 else None
    occurrence_col = col_names[4] if len(col_names) > 4 else None
    treatment_col = col_names[5] if len(col_names) > 5 else None

    cropdp_names = {}
    for idx, row in cropdp_df.iterrows():
        name = str(row[name_col]).strip()
        cropdp_names[name] = row

    matched_count = 0

    print("\n🔍 开始匹配病害...")

    for disease_folder in your_diseases:
        chinese_name = get_chinese_name(disease_folder)

        matched_row = None
        matched_key = None

        if chinese_name in cropdp_names:
            matched_row = cropdp_names[chinese_name]
            matched_key = chinese_name
        else:
            for name in cropdp_names:
                if chinese_name in name or name in chinese_name:
                    matched_row = cropdp_names[name]
                    matched_key = name
                    break

        if matched_row is not None:
            matched_count += 1
            knowledge[chinese_name] = {
                "disease_name": str(matched_row[name_col]) if pd.notna(matched_row[name_col]) else "",
                "english_name": str(matched_row[english_col]) if english_col and pd.notna(
                    matched_row[english_col]) else "",
                "symptoms": str(matched_row[symptom_col]) if symptom_col and pd.notna(matched_row[symptom_col]) else "",
                "occurrence": str(matched_row[occurrence_col]) if occurrence_col and pd.notna(
                    matched_row[occurrence_col]) else "",
                "treatment": str(matched_row[treatment_col]) if treatment_col and pd.notna(
                    matched_row[treatment_col]) else "",
                "source": "CropDP-KG (安徽省农业科学院/北京林业大学)",
                "matched_from": matched_key,
                "folder_name": disease_folder
            }
            print(f"  ✅ {chinese_name}")
        else:
            knowledge[chinese_name] = {
                "disease_name": chinese_name,
                "english_name": "",
                "symptoms": "待补充",
                "occurrence": "待补充",
                "treatment": "待补充",
                "source": "待补充",
                "matched_from": None,
                "folder_name": disease_folder
            }
            print(f"  ⚠️ 未匹配: {chinese_name}")

    print(f"\n匹配统计: {matched_count}/{len(your_diseases)} 成功匹配")
    return knowledge


def generate_formatted_knowledge(knowledge):
    """生成 app.py 可以直接使用的格式化知识库"""
    formatted = {}

    for disease_name, info in knowledge.items():
        if info.get('symptoms') and info['symptoms'] != "待补充":
            formatted[disease_name] = {
                "symptoms": info['symptoms'],
                "cause": info.get('occurrence', '暂无'),
                "prevention": "注意田间管理，合理轮作，选用抗病品种",
                "treatment": info.get('treatment', '暂无'),
                "chemicals": extract_chemicals(info.get('treatment', ''))
            }
        else:
            formatted[disease_name] = {
                "symptoms": info.get('symptoms', '暂无'),
                "cause": "待补充",
                "prevention": "建议咨询当地农技人员",
                "treatment": info.get('treatment', '待补充'),
                "chemicals": []
            }

    return formatted


def extract_chemicals(treatment_text):
    """从防治文本中提取药剂名称"""
    if not treatment_text or treatment_text == "待补充":
        return []

    common_chemicals = [
        "三唑酮", "戊唑醇", "烯唑醇", "苯醚甲环唑", "丙环唑",
        "吡唑醚菌酯", "肟菌酯", "嘧菌酯", "代森锰锌", "百菌清",
        "多菌灵", "甲基硫菌灵", "三环唑", "稻瘟灵", "春雷霉素"
    ]

    found = []
    for chemical in common_chemicals:
        if chemical in treatment_text:
            found.append(chemical)
    return found[:5]


def save_knowledge_base(knowledge, formatted_knowledge):
    """保存知识库"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 原始知识库已保存到: {OUTPUT_FILE}")

    with open(FORMATTED_FILE, "w", encoding="utf-8") as f:
        json.dump(formatted_knowledge, f, ensure_ascii=False, indent=2)
    print(f"✅ 格式化知识库已保存到: {FORMATTED_FILE}")


def main():
    print("=" * 60)
    print("CropDP-KG 知识库构建工具")
    print("=" * 60)

    print(f"\n📁 项目根目录: {PROJECT_ROOT}")
    print(f"📁 数据目录: {DATA_DIR}")
    print(f"📁 病害目录: {DISEASE_FOLDER}")
    print(f"📁 输出目录: {KNOWLEDGE_DIR}")

    your_diseases = get_your_diseases()
    if not your_diseases:
        print("❌ 未找到病害列表，请检查路径")
        return
    print(f"\n📋 共 {len(your_diseases)} 个病害类别")

    cropdp_df = load_cropdp_data()
    if cropdp_df is None:
        return

    knowledge = match_diseases(your_diseases, cropdp_df)
    formatted_knowledge = generate_formatted_knowledge(knowledge)
    save_knowledge_base(knowledge, formatted_knowledge)

    matched = sum(1 for v in knowledge.values() if v['source'] != "待补充")
    print(f"\n📊 最终统计: {matched}/{len(knowledge)} 匹配成功 ({matched / len(knowledge) * 100:.1f}%)")


if __name__ == "__main__":
    main()