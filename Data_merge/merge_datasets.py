import os
import shutil
from pathlib import Path

# ==================== 配置路径 ====================
# 15 Crop 数据集路径
SOURCE_ROOT = r"D:\Edge\15 Crop 45 Disease and Healthy Leaf dataset\15 Crop 45 Disease and Healthy Leaf dataset"

# PlantVillage 目标路径
TARGET_ROOT = r"D:\User\PycharmProjects\plant-health-ai-main\datasets\raw\color"

# ==================== 文件夹名称映射 ====================
# 格式: (源文件夹名, 目标文件夹名)
FOLDER_MAPPING = [
    # ===== 腰果 (Cashew) =====
    ("Cashew leaf miner", "Cashew___leaf_miner"),
    ("Cashew red rust", "Cashew___red_rust"),
    ("healthy_cashew", "Cashew___healthy"),

    # ===== 木薯 (Cassava) =====
    ("Cassava brown spot", "Cassava___brown_spot"),
    ("Cassava mosaic", "Cassava___mosaic"),
    ("healthy_cassava", "Cassava___healthy"),

    # ===== 辣椒 (Chili) =====
    ("Chili Healthy Leaf", "Chili___healthy"),
    ("Chilli Nutrition Deficiency", "Chili___nutrition_deficiency"),
    ("Chilli White spot", "Chili___white_spot"),

    # ===== 柑橘 (Citrus) - 已有，补充 =====
    ("Citrus Black spot", "Orange___Haunglongbing"),  # 合并到柑橘黄龙病
    ("Citrus canker", "Citrus___canker"),  # 新建
    ("Citrus Healthy", "Orange___healthy"),  # 合并到柑橘健康

    # ===== 棉花 (Cotton) =====
    ("Cotton Bacterial Blight", "Cotton___bacterial_blight"),
    ("Cotton Curl Virus", "Cotton___curl_virus"),
    ("Cotton Healthy Leaf", "Cotton___healthy"),

    # ===== 花生 (Groundnut) =====
    ("Ground healthy leaf", "Groundnut___healthy"),
    ("Ground late leaf spot", "Groundnut___late_leaf_spot"),
    ("Ground nutrition deficiency", "Groundnut___nutrition_deficiency"),

    # ===== 葡萄 (Grape) - 已有，补充 =====
    ("Grape__Black_rot", "Grape___Black_rot"),
    ("Grape__healthy", "Grape___healthy"),
    ("Grape__Leaf_blight", "Grape___Leaf_blight"),

    # ===== 玉米 (Maize) - 已有，补充 =====
    ("Maize leaf spot", "Maize___leaf_spot"),
    ("Maize streak virus", "Maize___streak_virus"),
    ("healthy_maize", "Maize___healthy"),

    # ===== 木瓜 (Papaya) =====
    ("Papaya BacterialSpot", "Papaya___bacterial_spot"),
    ("Papaya Healthy", "Papaya___healthy"),
    ("Papaya RingSpot", "Papaya___ring_spot"),

    # ===== 马铃薯 (Potato) - 已有，补充 =====
    ("Potato Early Blight", "Potato___Early_blight"),
    ("Potato Healthy", "Potato___healthy"),
    ("Potato Late Blight", "Potato___Late_blight"),

    # ===== 水稻 (Rice) =====
    ("Rice_Brown_Spot", "Rice___brown_spot"),
    ("Rice_Healthy", "Rice___healthy"),
    ("Rice_Leaf_Blast", "Rice___leaf_blast"),

    # ===== 大豆 (Soybean) - 已有，补充 =====
    ("Soyabean Caterpillar", "Soybean___caterpillar"),
    ("Soyabean Diabrotica speciosa", "Soybean___diabrotica"),
    ("Soybean Healthy", "Soybean___healthy"),

    # ===== 甘蔗 (Sugarcane) =====
    ("Sugarcane Brown Spot", "Sugarcane___brown_spot"),
    ("Sugarcane Grassy shoot", "Sugarcane___grassy_shoot"),
    ("Sugarcane Healthy Leaves", "Sugarcane___healthy"),

    # ===== 番茄 (Tomato) - 已有，补充 =====
    ("leaf blight_tomato", "Tomato___Early_blight"),
    ("septoria leaf spot_tomato", "Tomato___Septoria_leaf_spot"),
    ("healthy_tomato", "Tomato___healthy"),

    # ===== 小麦 (Wheat) =====
    ("Wheat_Brown Rust", "Wheat___brown_rust"),
    ("Wheat_Healthy", "Wheat___healthy"),
    ("Wheat_Yellow Rust", "Wheat___yellow_rust"),
]


# ==================== 工具函数 ====================
def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"  创建目录: {path}")


def copy_images(src_dir, dst_dir):
    """复制图片文件"""
    if not os.path.exists(src_dir):
        print(f"  ⚠️ 源目录不存在: {src_dir}")
        return 0

    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG', '.bmp', '.tiff'}

    copied_count = 0
    for file in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file)
        if os.path.isfile(src_file):
            ext = os.path.splitext(file)[1]
            if ext in image_extensions:
                dst_file = os.path.join(dst_dir, file)
                # 如果文件已存在，跳过
                if not os.path.exists(dst_file):
                    shutil.copy2(src_file, dst_file)
                    copied_count += 1

    return copied_count


def merge_images(src_dir, dst_dir):
    """合并图片（不覆盖已有文件）"""
    if not os.path.exists(src_dir):
        print(f"  ⚠️ 源目录不存在: {src_dir}")
        return 0

    ensure_dir(dst_dir)

    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG', '.bmp', '.tiff'}

    copied_count = 0
    for file in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file)
        if os.path.isfile(src_file):
            ext = os.path.splitext(file)[1]
            if ext in image_extensions:
                dst_file = os.path.join(dst_dir, file)
                if not os.path.exists(dst_file):
                    shutil.copy2(src_file, dst_file)
                    copied_count += 1

    return copied_count


# ==================== 主函数 ====================
def main():
    print("=" * 60)
    print("15 Crop 数据集合并工具")
    print("=" * 60)

    # 检查源路径是否存在
    if not os.path.exists(SOURCE_ROOT):
        print(f"\n❌ 错误：源路径不存在")
        print(f"   {SOURCE_ROOT}")
        print("\n请修改脚本中的 SOURCE_ROOT 为正确的路径")
        return

    print(f"\n✅ 源路径: {SOURCE_ROOT}")
    print(f"✅ 目标路径: {TARGET_ROOT}")

    # 统计
    total_copied = 0
    success_count = 0
    fail_count = 0

    print("\n" + "-" * 60)
    print("开始整理...")
    print("-" * 60)

    for src_name, dst_name in FOLDER_MAPPING:
        src_path = os.path.join(SOURCE_ROOT, src_name)
        dst_path = os.path.join(TARGET_ROOT, dst_name)

        if os.path.exists(src_path):
            # 复制图片
            copied = merge_images(src_path, dst_path)
            total_copied += copied
            success_count += 1
            print(f"✅ {src_name:30s} → {dst_name:35s} (复制 {copied} 张)")
        else:
            fail_count += 1
            print(f"⚠️ 未找到: {src_name}")

    print("-" * 60)
    print(f"\n📊 整理完成统计:")
    print(f"   成功处理: {success_count} 个文件夹")
    print(f"   未找到: {fail_count} 个文件夹")
    print(f"   新复制图片: {total_copied} 张")

    # 统计目标目录中的类别总数
    print("\n" + "-" * 60)
    print("目标目录统计:")
    print("-" * 60)

    if os.path.exists(TARGET_ROOT):
        categories = [d for d in os.listdir(TARGET_ROOT)
                      if os.path.isdir(os.path.join(TARGET_ROOT, d))]
        print(f"   总类别数: {len(categories)}")

        # 统计新增的作物类别
        new_crops = [
            "Cashew", "Cassava", "Chili", "Cotton", "Groundnut",
            "Papaya", "Rice", "Sugarcane", "Wheat", "Citrus", "Maize"
        ]
        print(f"   新增作物: {', '.join(new_crops)}")

    print("\n✅ 整理完成！现在可以运行训练脚本了。")


if __name__ == "__main__":
    main()