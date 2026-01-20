"""
示例 2: 批量生成不同pitch参数的版图
Example 2: Batch generation of layouts with varying pitch parameters
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_recognizer import LayoutRecognizer, GeometricFeature, LayoutParameters
from gds_writer import GDSWriter
import numpy as np


def create_single_rectangle():
    """创建单个矩形特征 / Create a single rectangle feature"""
    width = 50
    height = 50
    
    vertices = [
        (0, 0),
        (width, 0),
        (width, height),
        (0, height)
    ]
    
    feature = GeometricFeature(
        shape_type='rectangle',
        vertices=vertices,
        centroid=(width/2, height/2),
        area=width * height,
        perimeter=2 * (width + height),
        bounding_box=(0, 0, width, height),
        properties={'num_vertices': 4, 'aspect_ratio': width/height}
    )
    
    return [feature]


def main():
    print("=" * 70)
    print("示例 2: 批量生成不同pitch参数的版图")
    print("Example 2: Batch Generation with Varying Pitch Parameters")
    print("=" * 70)
    
    # 创建单个矩形特征
    print("\n1. 创建基础图案... / Creating base pattern...")
    features = create_single_rectangle()
    
    # 初始化识别器
    recognizer = LayoutRecognizer()
    
    # 定义批量参数范围
    print("\n2. 定义批量参数范围... / Defining batch parameter ranges...")
    batch_params = {
        'pitch_x_range': (100, 300, 50),  # 从100到300，步长50
        'pitch_y_range': (100, 300, 50),
    }
    print(f"   Pitch X范围: {batch_params['pitch_x_range']}")
    print(f"   Pitch Y范围: {batch_params['pitch_y_range']}")
    
    # 批量生成
    print("\n3. 批量生成版图... / Batch generating layouts...")
    layouts = recognizer.batch_generate(features, batch_params)
    
    # 写入GDS文件
    print("\n4. 写入GDS文件... / Writing GDS files...")
    gds_writer = GDSWriter()
    filenames = gds_writer.write_batch("examples/batch", layouts)
    
    print("\n" + "=" * 70)
    print(f"批量生成完成! 共生成 {len(filenames)} 个GDS文件")
    print(f"Batch generation completed! Generated {len(filenames)} GDS files")
    print("=" * 70)


if __name__ == "__main__":
    main()
