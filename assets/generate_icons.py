#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成BOM管理系统导航栏图标 (20x20 莫兰迪棕色)"""

from PIL import Image, ImageDraw

C = "#5D4E37"  # 莫兰迪暖棕色
S = 20          # 尺寸

def save(img, name):
    img.save(f"I:/采购管理系统/BOM管理系统1.0/assets/{name}")

# ── nav_product_info.png ── 成品信息（标签/文档图标）
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rectangle([3, 2, 17, 18], outline=C, width=1, fill=None)
d.line([6, 6, 14, 6], fill=C, width=1)
d.line([6, 9, 14, 9], fill=C, width=1)
d.line([6, 12, 11, 12], fill=C, width=1)
save(img, "nav_product_info.png")

# ── nav_product_bom.png ── 成品BOM（树形/层级结构图标）
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
# 顶层节点
d.rectangle([7, 2, 13, 5], outline=C, fill=C)
# 连接线
d.line([10, 5, 10, 7], fill=C, width=1)
d.line([4, 7, 16, 7], fill=C, width=1)
# 左子节点
d.line([4, 7, 4, 9], fill=C, width=1)
d.rectangle([2, 9, 6, 12], outline=C, fill=C)
# 右子节点
d.line([16, 7, 16, 9], fill=C, width=1)
d.rectangle([14, 9, 18, 12], outline=C, fill=C)
# 左子节点的子节点
d.line([4, 12, 4, 14], fill=C, width=1)
d.rectangle([2, 14, 6, 17], outline=C, fill=C)
save(img, "nav_product_bom.png")

print("导航图标生成完成！")
