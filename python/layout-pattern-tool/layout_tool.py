#!/usr/bin/env python3
"""
Layout Pattern Recognition Tool - Main Entry Point

版图模式识别工具 - 主入口
"""

import argparse
import sys
from pathlib import Path

from layout_recognizer import LayoutRecognizer
from gds_writer import GDSWriter
from oas_writer import OASWriter
from config_generator import PatchConfigGenerator, GaugeConfigGenerator, PeriodicExtensionConfig


def main():
    parser = argparse.ArgumentParser(
        description='Layout Pattern Recognition and GDS/OAS Generation Tool\n'
                    '版图模式识别和GDS/OAS生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--input', '-i', type=str,
                       help='Input image file path / 输入图像文件路径')
    parser.add_argument('--output', '-o', type=str, default='output',
                       help='Output file basename / 输出文件基础名称')
    parser.add_argument('--format', '-f', type=str, choices=['gds', 'oas', 'both'],
                       default='both',
                       help='Output format / 输出格式 (default: both)')
    parser.add_argument('--config', '-c', action='store_true',
                       help='Generate configuration files / 生成配置文件')
    parser.add_argument('--batch', '-b', action='store_true',
                       help='Batch generation mode / 批量生成模式')
    parser.add_argument('--pitch-x-range', type=str,
                       help='Pitch X range for batch: start,end,step / X方向pitch范围: 起始,结束,步长')
    parser.add_argument('--pitch-y-range', type=str,
                       help='Pitch Y range for batch: start,end,step / Y方向pitch范围: 起始,结束,步长')
    parser.add_argument('--periodic-extension', action='store_true',
                       help='Enable periodic extension for non-periodic layouts / 启用非周期性版图的周期延拓')
    parser.add_argument('--extension-x', type=float, default=200.0,
                       help='Periodic extension period in X direction / X方向延拓周期')
    parser.add_argument('--extension-y', type=float, default=200.0,
                       help='Periodic extension period in Y direction / Y方向延拓周期')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Layout Pattern Recognition Tool")
    print("版图模式识别工具")
    print("=" * 70)
    
    # Initialize recognizer
    recognizer = LayoutRecognizer()
    
    # Load and process image if provided
    if args.input:
        print(f"\n加载图像 / Loading image: {args.input}")
        try:
            image = recognizer.load_image(args.input)
            print("图像加载成功 / Image loaded successfully")
            
            # Detect features
            print("\n检测几何特征 / Detecting geometric features...")
            features = recognizer.detect_features(image)
            print(f"检测到 {len(features)} 个特征 / Detected {len(features)} features")
            
        except Exception as e:
            print(f"错误 / Error: {e}")
            sys.exit(1)
    else:
        print("\n未提供输入图像，使用示例模式 / No input image provided, using example mode")
        print("运行示例程序请使用: python examples/example1_basic.py")
        print("To run examples: python examples/example1_basic.py")
        sys.exit(0)
    
    # Detect periodicity
    print("\n检测周期性 / Detecting periodicity...")
    periodicity = recognizer.detect_periodicity(features)
    
    if periodicity.has_x_periodicity or periodicity.has_y_periodicity:
        print("检测到周期性 / Periodicity detected:")
        if periodicity.has_x_periodicity:
            print(f"  X方向周期 / X period: {periodicity.x_period:.2f}")
        if periodicity.has_y_periodicity:
            print(f"  Y方向周期 / Y period: {periodicity.y_period:.2f}")
    else:
        print("未检测到周期性 / No periodicity detected")
    
    # Define parameters
    print("\n定义参数 / Defining parameters...")
    params = recognizer.interactive_parameter_definition(features)
    
    # Batch generation mode
    if args.batch:
        print("\n批量生成模式 / Batch generation mode")
        
        # Parse pitch ranges
        def parse_range(range_str):
            if range_str:
                parts = [float(x) for x in range_str.split(',')]
                if len(parts) == 3:
                    return tuple(parts)
            return (100, 300, 50)  # default
        
        batch_params = {
            'pitch_x_range': parse_range(args.pitch_x_range),
            'pitch_y_range': parse_range(args.pitch_y_range),
        }
        
        print(f"Pitch X范围: {batch_params['pitch_x_range']}")
        print(f"Pitch Y范围: {batch_params['pitch_y_range']}")
        
        layouts = recognizer.batch_generate(features, batch_params)
        
        # Write batch files
        if args.format in ['gds', 'both']:
            gds_writer = GDSWriter()
            gds_writer.write_batch(args.output, layouts)
        
        if args.format in ['oas', 'both']:
            oas_writer = OASWriter()
            oas_writer.write_batch(args.output, layouts)
    
    else:
        # Single output mode
        if args.format in ['gds', 'both']:
            print(f"\n生成GDS文件 / Generating GDS file: {args.output}.gds")
            gds_writer = GDSWriter()
            gds_writer.write(f"{args.output}.gds", features, params)
        
        if args.format in ['oas', 'both']:
            print(f"\n生成OAS文件 / Generating OAS file: {args.output}.oas")
            oas_writer = OASWriter()
            oas_writer.write(f"{args.output}.oas", features, params)
    
    # Generate configuration files
    if args.config:
        print("\n生成配置文件 / Generating configuration files...")
        
        patch_gen = PatchConfigGenerator()
        patch_gen.generate(f"{args.output}_patch.yaml", features, params, periodicity)
        
        gauge_gen = GaugeConfigGenerator()
        gauge_gen.generate(f"{args.output}_gauge.cw", features, params, periodicity)
    
    # Generate periodic extension config for non-periodic layouts
    if args.periodic_extension and not (periodicity.has_x_periodicity or periodicity.has_y_periodicity):
        print("\n生成周期延拓配置 / Generating periodic extension configuration...")
        extension_config = PeriodicExtensionConfig()
        extension_config.generate(
            f"{args.output}_extension.yaml",
            features,
            args.extension_x,
            args.extension_y
        )
    
    print("\n" + "=" * 70)
    print("处理完成 / Processing completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
