"""
示例 3: 非周期性版图的周期延拓
Example 3: Periodic extension for non-periodic layouts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_recognizer import LayoutRecognizer, GeometricFeature, LayoutParameters
from config_generator import PeriodicExtensionConfig
import numpy as np


def create_irregular_pattern():
    """
    创建一个不规则的非周期性图案
    Create an irregular non-periodic pattern
    """
    features = []
    
    # 创建不同大小和位置的矩形
    # Create rectangles of different sizes and positions
    rectangles = [
        (10, 10, 50, 50),    # (x, y, width, height)
        (80, 30, 40, 60),
        (30, 100, 70, 30),
    ]
    
    for x, y, width, height in rectangles:
        vertices = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height)
        ]
        
        feature = GeometricFeature(
            shape_type='rectangle',
            vertices=vertices,
            centroid=(x + width/2, y + height/2),
            area=width * height,
            perimeter=2 * (width + height),
            bounding_box=(x, y, x + width, y + height),
            properties={'num_vertices': 4, 'aspect_ratio': width/height}
        )
        
        features.append(feature)
    
    return features


def main():
    print("=" * 70)
    print("示例 3: 非周期性版图的周期延拓")
    print("Example 3: Periodic Extension for Non-periodic Layouts")
    print("=" * 70)
    
    # 创建非周期性图案
    print("\n1. 创建非周期性图案... / Creating non-periodic pattern...")
    features = create_irregular_pattern()
    print(f"   创建了 {len(features)} 个几何特征 / Created {len(features)} geometric features")
    
    # 检测周期性（应该不存在）
    print("\n2. 检测周期性... / Detecting periodicity...")
    recognizer = LayoutRecognizer()
    periodicity = recognizer.detect_periodicity(features)
    print(f"   X方向周期性: {periodicity.has_x_periodicity}")
    print(f"   Y方向周期性: {periodicity.has_y_periodicity}")
    
    # 定义周期延拓参数
    print("\n3. 设置周期延拓参数... / Setting periodic extension parameters...")
    extension_x = 200.0
    extension_y = 200.0
    print(f"   X方向延拓周期: {extension_x}")
    print(f"   Y方向延拓周期: {extension_y}")
    
    # 生成周期延拓配置
    print("\n4. 生成周期延拓配置... / Generating periodic extension config...")
    extension_config = PeriodicExtensionConfig()
    extension_config.generate(
        "examples/example3_extension.yaml",
        features,
        extension_x,
        extension_y
    )
    
    print("\n" + "=" * 70)
    print("周期延拓配置已生成!")
    print("Periodic extension configuration generated!")
    print("=" * 70)


if __name__ == "__main__":
    main()
