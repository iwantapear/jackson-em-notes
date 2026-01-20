"""
GDS File Writer Module

GDS格式文件生成模块
GDS format file generation module
"""

import gdspy
from typing import List, Optional
from .layout_recognizer import GeometricFeature, LayoutParameters


class GDSWriter:
    """
    GDS文件写入器
    GDS file writer
    """
    
    def __init__(self, unit: float = 1e-6, precision: float = 1e-9):
        """
        初始化GDS写入器
        Initialize GDS writer
        
        Args:
            unit: 单位 (默认1微米) / Unit (default 1 micron)
            precision: 精度 / Precision
        """
        self.unit = unit
        self.precision = precision
        
    def write(self, filename: str, features: List[GeometricFeature], 
              params: LayoutParameters, cell_name: str = "LAYOUT") -> None:
        """
        写入GDS文件
        Write GDS file
        
        Args:
            filename: 输出文件名 / Output filename
            features: 几何特征列表 / List of geometric features
            params: 版图参数 / Layout parameters
            cell_name: 单元名称 / Cell name
        """
        # Create library
        lib = gdspy.GdsLibrary()
        
        # Create cell
        cell = lib.new_cell(cell_name)
        
        # Add each feature as a polygon
        for feature in features:
            # Convert vertices to gdspy format
            points = feature.vertices
            
            # Create polygon
            polygon = gdspy.Polygon(
                points,
                layer=params.layer if params else 0,
                datatype=params.datatype if params else 0
            )
            
            cell.add(polygon)
        
        # Write to file
        lib.write_gds(filename, unit=self.unit, precision=self.precision)
        print(f"GDS文件已保存到: {filename} / GDS file saved to: {filename}")
    
    def write_with_periodicity(self, filename: str, features: List[GeometricFeature],
                              params: LayoutParameters, 
                              repeat_x: int = 1, repeat_y: int = 1,
                              cell_name: str = "LAYOUT") -> None:
        """
        写入具有周期性的GDS文件
        Write GDS file with periodicity
        
        Args:
            filename: 输出文件名 / Output filename
            features: 几何特征列表 / List of geometric features
            params: 版图参数 / Layout parameters
            repeat_x: X方向重复次数 / X-direction repeat count
            repeat_y: Y方向重复次数 / Y-direction repeat count
            cell_name: 单元名称 / Cell name
        """
        lib = gdspy.GdsLibrary()
        
        # Create unit cell
        unit_cell = lib.new_cell(cell_name + "_UNIT")
        
        for feature in features:
            polygon = gdspy.Polygon(
                feature.vertices,
                layer=params.layer if params else 0,
                datatype=params.datatype if params else 0
            )
            unit_cell.add(polygon)
        
        # Create main cell with array
        main_cell = lib.new_cell(cell_name)
        
        pitch_x = params.pitch_x if params and params.pitch_x else 100
        pitch_y = params.pitch_y if params and params.pitch_y else 100
        
        # Create array of unit cells
        for i in range(repeat_x):
            for j in range(repeat_y):
                ref = gdspy.CellReference(
                    unit_cell,
                    origin=(i * pitch_x, j * pitch_y)
                )
                main_cell.add(ref)
        
        lib.write_gds(filename, unit=self.unit, precision=self.precision)
        print(f"带周期性的GDS文件已保存到: {filename} / Periodic GDS file saved to: {filename}")
        print(f"重复次数: X={repeat_x}, Y={repeat_y} / Repeat count: X={repeat_x}, Y={repeat_y}")
    
    def write_batch(self, base_filename: str, layouts: List[dict]) -> List[str]:
        """
        批量写入GDS文件
        Batch write GDS files
        
        Args:
            base_filename: 基础文件名 / Base filename
            layouts: 版图列表 / List of layouts
            
        Returns:
            生成的文件名列表 / List of generated filenames
        """
        filenames = []
        
        for i, layout in enumerate(layouts):
            features = layout['features']
            params = layout['params']
            name = layout.get('name', f'layout_{i}')
            
            filename = f"{base_filename}_{name}.gds"
            self.write(filename, features, params, name)
            filenames.append(filename)
        
        print(f"批量生成了 {len(filenames)} 个GDS文件 / Batch generated {len(filenames)} GDS files")
        return filenames
