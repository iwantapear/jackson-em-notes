"""
Layout Pattern Recognition and GDS/OAS Generation Tool

本模块实现了从图像识别几何特征并转换为GDS/OAS版图文件的功能。
This module implements pattern recognition and conversion to GDS/OAS layout files.
"""

__version__ = "1.0.0"
__author__ = "Layout Tool Contributors"

from .layout_recognizer import LayoutRecognizer
from .gds_writer import GDSWriter
from .oas_writer import OASWriter
from .config_generator import PatchConfigGenerator, GaugeConfigGenerator

__all__ = [
    'LayoutRecognizer',
    'GDSWriter',
    'OASWriter',
    'PatchConfigGenerator',
    'GaugeConfigGenerator',
]
