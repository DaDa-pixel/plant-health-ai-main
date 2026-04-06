# disease_names_cn.py
# 病害名称中英文映射表

DISEASE_NAMES_CN = {
    # ========== 苹果 ==========
    "Apple___Apple_scab": "苹果疮痂病",
    "Apple___Black_rot": "苹果黑腐病",
    "Apple___Cedar_apple_rust": "苹果雪松锈病",
    "Apple___healthy": "苹果健康",

    # ========== 蓝莓 ==========
    "Blueberry___healthy": "蓝莓健康",

    # ========== 樱桃 ==========
    "Cherry_(including_sour)___Powdery_mildew": "樱桃白粉病",
    "Cherry_(including_sour)___healthy": "樱桃健康",

    # ========== 玉米 ==========
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "玉米灰斑病",
    "Corn_(maize)___Common_rust_": "玉米普通锈病",
    "Corn_(maize)___Northern_Leaf_Blight": "玉米大斑病",
    "Corn_(maize)___healthy": "玉米健康",
    "Maize___leaf_spot": "玉米叶斑病",
    "Maize___streak_virus": "玉米条纹病毒病",
    "Maize___healthy": "玉米健康",

    # ========== 葡萄 ==========
    "Grape___Black_rot": "葡萄黑腐病",
    "Grape___Esca_(Black_Measles)": "葡萄黑麻疹病",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "葡萄叶枯病",
    "Grape___healthy": "葡萄健康",

    # ========== 柑橘 ==========
    "Orange___Haunglongbing_(Citrus_greening)": "柑橘黄龙病",
    "Citrus___canker": "柑橘溃疡病",
    "Orange___healthy": "柑橘健康",

    # ========== 桃子 ==========
    "Peach___Bacterial_spot": "桃细菌性斑点病",
    "Peach___healthy": "桃健康",

    # ========== 甜椒 ==========
    "Pepper,_bell___Bacterial_spot": "甜椒细菌性斑点病",
    "Pepper,_bell___healthy": "甜椒健康",

    # ========== 马铃薯 ==========
    "Potato___Early_blight": "马铃薯早疫病",
    "Potato___Late_blight": "马铃薯晚疫病",
    "Potato___healthy": "马铃薯健康",

    # ========== 树莓 ==========
    "Raspberry___healthy": "树莓健康",

    # ========== 大豆 ==========
    "Soybean___healthy": "大豆健康",
    "Soybean___caterpillar": "大豆毛虫危害",
    "Soybean___diabrotica": "大豆玉米萤叶甲",

    # ========== 南瓜 ==========
    "Squash___Powdery_mildew": "南瓜白粉病",

    # ========== 草莓 ==========
    "Strawberry___Leaf_scorch": "草莓叶焦病",
    "Strawberry___healthy": "草莓健康",

    # ========== 番茄 ==========
    "Tomato___Bacterial_spot": "番茄细菌性斑点病",
    "Tomato___Early_blight": "番茄早疫病",
    "Tomato___Late_blight": "番茄晚疫病",
    "Tomato___Leaf_Mold": "番茄叶霉病",
    "Tomato___Septoria_leaf_spot": "番茄叶斑病",
    "Tomato___Spider_mites Two-spotted_spider_mite": "番茄蜘蛛螨",
    "Tomato___Target_Spot": "番茄靶斑病",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "番茄黄化曲叶病毒病",
    "Tomato___Tomato_mosaic_virus": "番茄花叶病毒病",
    "Tomato___healthy": "番茄健康",

    # ========== 腰果 ==========
    "Cashew___leaf_miner": "腰果潜叶虫",
    "Cashew___red_rust": "腰果红锈病",
    "Cashew___healthy": "腰果健康",

    # ========== 木薯 ==========
    "Cassava___brown_spot": "木薯褐斑病",
    "Cassava___mosaic": "木薯花叶病",
    "Cassava___healthy": "木薯健康",

    # ========== 辣椒 ==========
    "Chili___healthy": "辣椒健康",
    "Chili___nutrition_deficiency": "辣椒营养缺乏",
    "Chili___white_spot": "辣椒白斑病",

    # ========== 棉花 ==========
    "Cotton___bacterial_blight": "棉花细菌性枯萎病",
    "Cotton___curl_virus": "棉花曲叶病毒病",
    "Cotton___healthy": "棉花健康",

    # ========== 花生 ==========
    "Groundnut___healthy": "花生健康",
    "Groundnut___late_leaf_spot": "花生晚叶斑病",
    "Groundnut___nutrition_deficiency": "花生营养缺乏",

    # ========== 木瓜 ==========
    "Papaya___bacterial_spot": "木瓜细菌性斑点病",
    "Papaya___healthy": "木瓜健康",
    "Papaya___ring_spot": "木瓜环斑病",

    # ========== 水稻 ==========
    "Rice___brown_spot": "水稻褐斑病",
    "Rice___healthy": "水稻健康",
    "Rice___leaf_blast": "水稻稻瘟病",

    # ========== 甘蔗 ==========
    "Sugarcane___brown_spot": "甘蔗褐斑病",
    "Sugarcane___grassy_shoot": "甘蔗丛芽病",
    "Sugarcane___healthy": "甘蔗健康",

    # ========== 小麦 ==========
    "Wheat___brown_rust": "小麦褐锈病",
    "Wheat___healthy": "小麦健康",
    "Wheat___yellow_rust": "小麦条锈病",
}


def get_chinese_name(english_name):
    """将英文类别名称转换为中文"""
    return DISEASE_NAMES_CN.get(english_name, english_name.replace('_', ' '))