import requests
import time
import json
from bs4 import BeautifulSoup
from pathlib import Path

# ==================== 配置 ====================
# 未匹配的病害列表
MISSING_DISEASES = [
    "苹果疮痂病", "苹果雪松锈病", "苹果健康", "蓝莓健康",
    "腰果健康", "腰果潜叶虫", "腰果红锈病", "木薯褐斑病", "木薯健康", "木薯花叶病",
    "樱桃健康", "辣椒健康", "辣椒营养缺乏", "玉米普通锈病", "玉米健康",
    "棉花细菌性枯萎病", "棉花曲叶病毒病", "棉花健康",
    "葡萄黑麻疹病", "葡萄叶枯病", "葡萄健康", "花生健康", "花生晚叶斑病", "花生营养缺乏",
    "玉米叶斑病", "玉米条纹病毒病", "柑橘健康", "木瓜细菌性斑点病", "木瓜健康", "木瓜环斑病",
    "桃细菌性斑点病", "桃健康", "甜椒细菌性斑点病", "甜椒健康",
    "马铃薯健康", "树莓健康", "大豆毛虫危害", "大豆玉米萤叶甲", "大豆健康",
    "草莓叶焦病", "草莓健康", "甘蔗褐斑病", "甘蔗丛芽病", "甘蔗健康",
    "番茄细菌性斑点病", "番茄叶斑病", "番茄蜘蛛螨", "番茄靶斑病", "番茄黄化曲叶病毒病", "番茄健康",
    "Wheat Brown Rust", "Wheat Healthy", "Wheat Yellow Rust"
]

# 文件路径
EXISTING_KNOWLEDGE = Path("knowledge_base/disease_knowledge.json")
EXISTING_FORMATTED = Path("knowledge_base/disease_knowledge_formatted.json")
OUTPUT_KNOWLEDGE = Path("knowledge_base/disease_knowledge_updated.json")
OUTPUT_FORMATTED = Path("knowledge_base/disease_knowledge_formatted_updated.json")

# 安徽农科院数据库URL模板（直接通过ID访问）
# 根据你提供的爬虫文件，数据从 id=1 到 id=3523
BASE_URL = "http://bcch.ahnw.cn/CropContent.aspx?id={}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def load_existing_knowledge():
    """加载现有的知识库"""
    knowledge = {}
    formatted = {}

    if EXISTING_KNOWLEDGE.exists():
        with open(EXISTING_KNOWLEDGE, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)
        print(f"加载现有知识库: {len(knowledge)} 条")

    if EXISTING_FORMATTED.exists():
        with open(EXISTING_FORMATTED, 'r', encoding='utf-8') as f:
            formatted = json.load(f)

    return knowledge, formatted


def get_disease_by_id(disease_id):
    """根据ID获取病害详细信息"""
    url = BASE_URL.format(disease_id)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = 'gbk'
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 提取信息
        name_zh = soup.find(attrs={"id": "lblNameZHCN"})
        name_en = soup.find(attrs={"id": "lblNameEng"})
        damage_sym = soup.find(attrs={"id": "lblDamageSym"})
        o_factor = soup.find(attrs={"id": "lblOFactor"})
        c_method = soup.find(attrs={"id": "lblCMethod"})

        if name_zh and name_zh.get_text().strip():
            return {
                "name_zh": name_zh.get_text().strip(),
                "name_en": name_en.get_text().strip() if name_en else "",
                "symptoms": damage_sym.get_text().strip().replace("[为害症状]", "") if damage_sym else "",
                "occurrence": o_factor.get_text().strip().replace("[发生规律]", "") if o_factor else "",
                "treatment": c_method.get_text().strip().replace("[防治]", "") if c_method else ""
            }
        return None
    except Exception as e:
        return None


def crawl_all_diseases():
    """遍历所有ID，建立名称到信息的映射"""
    print("正在建立数据库索引...")
    disease_map = {}

    # 遍历ID 1 到 3523
    for i in range(1, 3524):
        info = get_disease_by_id(i)
        if info and info['name_zh']:
            disease_map[info['name_zh']] = info
            if i % 500 == 0:
                print(f"  已处理 {i} 条记录，当前索引 {len(disease_map)} 条")

        # 每50个请求暂停一下
        if i % 50 == 0:
            time.sleep(0.5)

    print(f"索引建立完成，共 {len(disease_map)} 条病害记录")
    return disease_map


def save_updated_knowledge(knowledge, formatted):
    """保存更新后的知识库"""
    with open(OUTPUT_KNOWLEDGE, 'w', encoding='utf-8') as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_FORMATTED, 'w', encoding='utf-8') as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 更新后的知识库已保存")


def extract_chemicals(treatment_text):
    """从防治文本中提取药剂名称"""
    if not treatment_text:
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


def main():
    print("=" * 60)
    print("未匹配病害爬取工具")
    print("=" * 60)

    # 加载现有知识库
    knowledge, formatted = load_existing_knowledge()

    # 先建立数据库索引（这一步需要时间，约10-15分钟）
    print("\n首次运行需要建立数据库索引，请耐心等待...")
    disease_map = crawl_all_diseases()

    # 保存索引到本地，下次可以直接加载
    with open("knowledge_base/disease_index.json", "w", encoding="utf-8") as f:
        # 只保存名称映射，不保存完整信息以节省空间
        index = {name: True for name in disease_map.keys()}
        json.dump(index, f, ensure_ascii=False, indent=2)

    # 匹配未匹配的病害
    new_count = 0
    for i, disease in enumerate(MISSING_DISEASES, 1):
        print(f"\n[{i}/{len(MISSING_DISEASES)}] 匹配: {disease}")

        # 跳过已存在的
        if disease in knowledge and knowledge[disease].get('source') != "待补充":
            print(f"  已存在，跳过")
            continue

        # 精确匹配
        if disease in disease_map:
            info = disease_map[disease]
            print(f"  ✅ 精确匹配到: {info['name_zh']}")

            # 更新原始知识库
            knowledge[disease] = {
                "disease_name": info.get('name_zh', disease),
                "english_name": info.get('name_en', ''),
                "symptoms": info.get('symptoms', ''),
                "occurrence": info.get('occurrence', ''),
                "treatment": info.get('treatment', ''),
                "source": "安徽农科院数据库 (bcch.ahnw.cn)",
                "matched_from": "exact_match"
            }

            # 更新格式化知识库
            formatted[disease] = {
                "symptoms": info.get('symptoms', ''),
                "cause": info.get('occurrence', ''),
                "prevention": "注意田间管理，合理轮作，选用抗病品种",
                "treatment": info.get('treatment', ''),
                "chemicals": extract_chemicals(info.get('treatment', ''))
            }
            new_count += 1
        else:
            # 模糊匹配
            found = False
            for name in disease_map:
                if disease in name or name in disease:
                    info = disease_map[name]
                    print(f"  ⚠️ 模糊匹配到: {name}")
                    knowledge[disease] = {
                        "disease_name": disease,
                        "english_name": info.get('name_en', ''),
                        "symptoms": info.get('symptoms', ''),
                        "occurrence": info.get('occurrence', ''),
                        "treatment": info.get('treatment', ''),
                        "source": "安徽农科院数据库 (bcch.ahnw.cn)",
                        "matched_from": f"fuzzy_match:{name}"
                    }
                    formatted[disease] = {
                        "symptoms": info.get('symptoms', ''),
                        "cause": info.get('occurrence', ''),
                        "prevention": "注意田间管理，合理轮作，选用抗病品种",
                        "treatment": info.get('treatment', ''),
                        "chemicals": extract_chemicals(info.get('treatment', ''))
                    }
                    new_count += 1
                    found = True
                    break

            if not found:
                print(f"  ❌ 未找到匹配")

    # 保存
    save_updated_knowledge(knowledge, formatted)

    # 统计
    total = len(knowledge)
    matched = sum(1 for v in knowledge.values() if v.get('source') != "待补充")
    print(f"\n{'=' * 60}")
    print(f"📊 最终统计:")
    print(f"   总记录数: {total}")
    print(f"   成功匹配: {matched}")
    print(f"   匹配率: {matched / total * 100:.1f}%")
    print(f"   本次新增: {new_count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()