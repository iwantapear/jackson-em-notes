"""
示例 1: 基本几何特征识别和GDS生成
Example 1: Basic geometric feature detection and GDS generation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_recognizer import LayoutRecognizer, GeometricFeature, LayoutParameters
from gds_writer import GDSWriter
from oas_writer import OASWriter
from config_generator import PatchConfigGenerator, GaugeConfigGenerator
import numpy as np


def create_test_pattern():
    """
    创建一个测试图案 (矩形阵列)
    Create a test pattern (rectangular array)
    """
    # 由于我们没有实际的图像文件，我们将手动创建几何特征
    # Since we don't have actual image files, we'll manually create geometric features
    
    features = []
    
    # 创建一个3x3的矩形阵列
    # Create a 3x3 rectangular array
    pitch_x = 200
    pitch_y = 200
    width = 50
    height = 50
    
    for i in range(3):
        for j in range(3):
            x = i * pitch_x
            y = j * pitch_y
            
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
    print("示例 1: 基本几何特征识别和GDS生成")
    print("Example 1: Basic Geometric Feature Detection and GDS Generation")
    print("=" * 70)
    
    # 创建测试图案
    print("\n1. 创建测试图案... / Creating test pattern...")
    features = create_test_pattern()
    print(f"   创建了 {len(features)} 个几何特征 / Created {len(features)} geometric features")
    
    # 初始化识别器
    print("\n2. 初始化识别器... / Initializing recognizer...")
    recognizer = LayoutRecognizer()
    recognizer.features = features
    
    # 检测周期性
    print("\n3. 检测周期性... / Detecting periodicity...")
    periodicity = recognizer.detect_periodicity(features)
    print(f"   X方向周期性: {periodicity.has_x_periodicity} / X-direction periodicity: {periodicity.has_x_periodicity}")
    print(f"   Y方向周期性: {periodicity.has_y_periodicity} / Y-direction periodicity: {periodicity.has_y_periodicity}")
    if periodicity.x_period:
        print(f"   X方向周期: {periodicity.x_period:.2f} / X-direction period: {periodicity.x_period:.2f}")
    if periodicity.y_period:
        print(f"   Y方向周期: {periodicity.y_period:.2f} / Y-direction period: {periodicity.y_period:.2f}")
    
    # 交互式参数定义
    print("\n4. 参数定义... / Defining parameters...")
    params = recognizer.interactive_parameter_definition(features)
    
    # 生成GDS文件
    print("\n5. 生成GDS文件... / Generating GDS file...")
    gds_writer = GDSWriter()
    gds_writer.write("examples/example1_basic.gds", features, params)
    
    # 生成带周期性的GDS文件
    print("\n6. 生成周期性GDS文件... / Generating periodic GDS file...")
    gds_writer.write_with_periodicity(
        "examples/example1_periodic.gds",
        features[:1],  # 只使用第一个特征作为单元
        params,
        repeat_x=3,
        repeat_y=3
    )
    
    # 生成OAS文件
    print("\n7. 生成OAS文件... / Generating OAS file...")
    oas_writer = OASWriter()
    oas_writer.write("examples/example1_basic.oas", features, params)
    
    # 生成配置文件
    print("\n8. 生成配置文件... / Generating configuration files...")
    patch_gen = PatchConfigGenerator()
    patch_gen.generate("examples/example1_patch.yaml", features, params, periodicity)
    
    gauge_gen = GaugeConfigGenerator()
    gauge_gen.generate("examples/example1_gauge.cw", features, params, periodicity)
    
    print("\n" + "=" * 70)
    print("示例完成! 生成的文件位于 examples/ 目录")
    print("Example completed! Generated files are in examples/ directory")
    print("=" * 70)


if __name__ == "__main__":
    main()
