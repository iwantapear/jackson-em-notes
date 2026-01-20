"""
Configuration File Generator Module

配置文件生成模块
Configuration file generation module
"""

import yaml
import json
from typing import List, Dict, Any
from .layout_recognizer import GeometricFeature, LayoutParameters, PeriodicityInfo


class PatchConfigGenerator:
    """
    Patch配置文件生成器
    Patch configuration file generator
    """
    
    def __init__(self):
        """初始化Patch配置生成器 / Initialize patch config generator"""
        pass
    
    def generate(self, filename: str, features: List[GeometricFeature],
                params: LayoutParameters, 
                periodicity: PeriodicityInfo = None,
                format: str = 'yaml') -> None:
        """
        生成Patch配置文件
        Generate patch configuration file
        
        Args:
            filename: 输出文件名 / Output filename
            features: 几何特征列表 / List of geometric features
            params: 版图参数 / Layout parameters
            periodicity: 周期性信息 / Periodicity information
            format: 文件格式 ('yaml' 或 'json') / File format ('yaml' or 'json')
        """
        config = self._create_patch_config(features, params, periodicity)
        
        if format == 'yaml':
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif format == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的格式: {format} / Unsupported format: {format}")
        
        print(f"Patch配置文件已保存到: {filename} / Patch config saved to: {filename}")
    
    def _create_patch_config(self, features: List[GeometricFeature],
                           params: LayoutParameters,
                           periodicity: PeriodicityInfo = None) -> Dict[str, Any]:
        """创建Patch配置字典 / Create patch configuration dictionary"""
        
        config = {
            'patch_config': {
                'version': '1.0',
                'description': '版图Patch配置 / Layout Patch Configuration',
                'features': []
            }
        }
        
        # Add feature information
        for i, feature in enumerate(features):
            feature_config = {
                'id': i,
                'type': feature.shape_type,
                'vertices': feature.vertices,
                'centroid': feature.centroid,
                'area': feature.area,
                'bounding_box': {
                    'x_min': feature.bounding_box[0],
                    'y_min': feature.bounding_box[1],
                    'x_max': feature.bounding_box[2],
                    'y_max': feature.bounding_box[3],
                }
            }
            config['patch_config']['features'].append(feature_config)
        
        # Add parameters
        if params:
            config['patch_config']['parameters'] = {
                'width': params.width,
                'height': params.height,
                'gap_x': params.gap_x,
                'gap_y': params.gap_y,
                'pitch_x': params.pitch_x,
                'pitch_y': params.pitch_y,
                'cd': params.cd,
                'layer': params.layer,
                'datatype': params.datatype,
            }
        
        # Add periodicity information
        if periodicity:
            config['patch_config']['periodicity'] = {
                'has_x_periodicity': periodicity.has_x_periodicity,
                'has_y_periodicity': periodicity.has_y_periodicity,
                'x_period': periodicity.x_period,
                'y_period': periodicity.y_period,
                'repeat_count_x': periodicity.repeat_count_x,
                'repeat_count_y': periodicity.repeat_count_y,
            }
        
        return config


class GaugeConfigGenerator:
    """
    Gauge (CW) 配置文件生成器
    Gauge (CW) configuration file generator
    """
    
    def __init__(self):
        """初始化Gauge配置生成器 / Initialize gauge config generator"""
        pass
    
    def generate(self, filename: str, features: List[GeometricFeature],
                params: LayoutParameters,
                periodicity: PeriodicityInfo = None) -> None:
        """
        生成Gauge配置文件
        Generate gauge configuration file
        
        Args:
            filename: 输出文件名 / Output filename
            features: 几何特征列表 / List of geometric features
            params: 版图参数 / Layout parameters
            periodicity: 周期性信息 / Periodicity information
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self._create_gauge_header())
            f.write(self._create_gauge_layout_info(features, params))
            f.write(self._create_gauge_features(features))
            
            if periodicity:
                f.write(self._create_gauge_periodicity(periodicity))
            
            f.write(self._create_gauge_footer())
        
        print(f"Gauge配置文件已保存到: {filename} / Gauge config saved to: {filename}")
    
    def _create_gauge_header(self) -> str:
        """创建Gauge文件头 / Create gauge file header"""
        return """# Gauge Configuration File
# 版图测量配置文件
# Auto-generated by Layout Pattern Recognition Tool

[HEADER]
VERSION = 1.0
DESCRIPTION = "Layout Gauge Configuration"

"""
    
    def _create_gauge_layout_info(self, features: List[GeometricFeature],
                                  params: LayoutParameters) -> str:
        """创建版图信息部分 / Create layout info section"""
        content = "[LAYOUT_INFO]\n"
        content += f"NUM_FEATURES = {len(features)}\n"
        
        if params:
            if params.width:
                content += f"WIDTH = {params.width}\n"
            if params.height:
                content += f"HEIGHT = {params.height}\n"
            if params.cd:
                content += f"CRITICAL_DIMENSION = {params.cd}\n"
            content += f"LAYER = {params.layer}\n"
            content += f"DATATYPE = {params.datatype}\n"
        
        content += "\n"
        return content
    
    def _create_gauge_features(self, features: List[GeometricFeature]) -> str:
        """创建特征部分 / Create features section"""
        content = "[FEATURES]\n"
        
        for i, feature in enumerate(features):
            content += f"# Feature {i}\n"
            content += f"FEATURE_{i}_TYPE = {feature.shape_type}\n"
            content += f"FEATURE_{i}_AREA = {feature.area}\n"
            content += f"FEATURE_{i}_PERIMETER = {feature.perimeter}\n"
            content += f"FEATURE_{i}_CENTROID_X = {feature.centroid[0]}\n"
            content += f"FEATURE_{i}_CENTROID_Y = {feature.centroid[1]}\n"
            content += f"FEATURE_{i}_NUM_VERTICES = {len(feature.vertices)}\n"
            content += "\n"
        
        return content
    
    def _create_gauge_periodicity(self, periodicity: PeriodicityInfo) -> str:
        """创建周期性部分 / Create periodicity section"""
        content = "[PERIODICITY]\n"
        content += f"HAS_X_PERIODICITY = {periodicity.has_x_periodicity}\n"
        content += f"HAS_Y_PERIODICITY = {periodicity.has_y_periodicity}\n"
        
        if periodicity.x_period:
            content += f"X_PERIOD = {periodicity.x_period}\n"
            content += f"X_REPEAT_COUNT = {periodicity.repeat_count_x}\n"
        
        if periodicity.y_period:
            content += f"Y_PERIOD = {periodicity.y_period}\n"
            content += f"Y_REPEAT_COUNT = {periodicity.repeat_count_y}\n"
        
        content += "\n"
        return content
    
    def _create_gauge_footer(self) -> str:
        """创建Gauge文件尾 / Create gauge file footer"""
        return """[END]
# End of Gauge Configuration File
"""


class PeriodicExtensionConfig:
    """
    非周期性版图的周期延拓配置
    Periodic extension configuration for non-periodic layouts
    """
    
    def __init__(self):
        """初始化周期延拓配置 / Initialize periodic extension config"""
        pass
    
    def generate(self, filename: str, features: List[GeometricFeature],
                extension_x: float, extension_y: float,
                format: str = 'yaml') -> None:
        """
        生成周期延拓配置
        Generate periodic extension configuration
        
        Args:
            filename: 输出文件名 / Output filename
            features: 几何特征列表 / List of geometric features
            extension_x: X方向延拓周期 / X-direction extension period
            extension_y: Y方向延拓周期 / Y-direction extension period
            format: 文件格式 / File format
        """
        config = {
            'periodic_extension': {
                'version': '1.0',
                'description': '非周期性版图的周期延拓配置 / Periodic Extension for Non-periodic Layout',
                'extension_period': {
                    'x': extension_x,
                    'y': extension_y,
                },
                'original_features': [
                    {
                        'type': f.shape_type,
                        'centroid': f.centroid,
                        'bounding_box': {
                            'x_min': f.bounding_box[0],
                            'y_min': f.bounding_box[1],
                            'x_max': f.bounding_box[2],
                            'y_max': f.bounding_box[3],
                        }
                    } for f in features
                ],
                'extension_instructions': {
                    'method': 'periodic_replication',
                    'description': '使用周期性复制进行延拓 / Use periodic replication for extension',
                }
            }
        }
        
        if format == 'yaml':
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif format == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"周期延拓配置已保存到: {filename} / Periodic extension config saved to: {filename}")
