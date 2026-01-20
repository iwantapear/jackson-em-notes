"""
OAS File Writer Module

OAS格式文件生成模块
OAS format file generation module
"""

from typing import List, Optional
from .layout_recognizer import GeometricFeature, LayoutParameters


class OASWriter:
    """
    OAS文件写入器
    OAS file writer
    
    注意: 完整的OAS支持需要klayout或其他专门库
    Note: Full OAS support requires klayout or other specialized libraries
    """
    
    def __init__(self):
        """初始化OAS写入器 / Initialize OAS writer"""
        self.use_klayout = self._check_klayout()
        
    def _check_klayout(self) -> bool:
        """检查klayout是否可用 / Check if klayout is available"""
        try:
            import pya
            return True
        except ImportError:
            print("警告: klayout未安装，将使用替代方法 / Warning: klayout not installed, using alternative method")
            return False
    
    def write(self, filename: str, features: List[GeometricFeature],
              params: LayoutParameters, cell_name: str = "LAYOUT") -> None:
        """
        写入OAS文件
        Write OAS file
        
        Args:
            filename: 输出文件名 / Output filename
            features: 几何特征列表 / List of geometric features
            params: 版图参数 / Layout parameters
            cell_name: 单元名称 / Cell name
        """
        if self.use_klayout:
            self._write_with_klayout(filename, features, params, cell_name)
        else:
            self._write_fallback(filename, features, params, cell_name)
    
    def _write_with_klayout(self, filename: str, features: List[GeometricFeature],
                           params: LayoutParameters, cell_name: str) -> None:
        """使用klayout写入OAS文件 / Write OAS file using klayout"""
        try:
            import pya
            
            # Create layout
            layout = pya.Layout()
            
            # Create cell
            cell = layout.create_cell(cell_name)
            
            # Get layer
            layer_idx = layout.layer(params.layer if params else 0, 
                                    params.datatype if params else 0)
            
            # Add polygons
            for feature in features:
                # Convert vertices to klayout points
                points = [pya.Point(int(x * 1000), int(y * 1000)) 
                         for x, y in feature.vertices]
                
                # Create polygon
                poly = pya.Polygon(points)
                cell.shapes(layer_idx).insert(poly)
            
            # Write OAS file
            layout.write(filename)
            print(f"OAS文件已保存到: {filename} / OAS file saved to: {filename}")
            
        except Exception as e:
            print(f"使用klayout写入失败: {e} / Failed to write with klayout: {e}")
            self._write_fallback(filename, features, params, cell_name)
    
    def _write_fallback(self, filename: str, features: List[GeometricFeature],
                       params: LayoutParameters, cell_name: str) -> None:
        """
        备用方法: 写入OAS格式的文本描述
        Fallback: Write OAS format text description
        """
        with open(filename.replace('.oas', '.oas.txt'), 'w') as f:
            f.write(f"OAS Layout Description\n")
            f.write(f"Cell: {cell_name}\n")
            f.write(f"Layer: {params.layer if params else 0}\n")
            f.write(f"Datatype: {params.datatype if params else 0}\n")
            f.write(f"\n")
            
            for i, feature in enumerate(features):
                f.write(f"Feature {i}: {feature.shape_type}\n")
                f.write(f"  Vertices: {feature.vertices}\n")
                f.write(f"  Area: {feature.area}\n")
                f.write(f"\n")
        
        print(f"OAS描述文件已保存到: {filename}.txt / OAS description saved to: {filename}.txt")
        print(f"提示: 安装klayout以生成真正的OAS文件 / Tip: Install klayout to generate actual OAS files")
    
    def write_with_periodicity(self, filename: str, features: List[GeometricFeature],
                              params: LayoutParameters,
                              repeat_x: int = 1, repeat_y: int = 1,
                              cell_name: str = "LAYOUT") -> None:
        """
        写入具有周期性的OAS文件
        Write OAS file with periodicity
        
        Args:
            filename: 输出文件名 / Output filename
            features: 几何特征列表 / List of geometric features
            params: 版图参数 / Layout parameters
            repeat_x: X方向重复次数 / X-direction repeat count
            repeat_y: Y方向重复次数 / Y-direction repeat count
            cell_name: 单元名称 / Cell name
        """
        if self.use_klayout:
            self._write_periodic_with_klayout(filename, features, params, 
                                             repeat_x, repeat_y, cell_name)
        else:
            # For fallback, just mention the periodicity in description
            with open(filename.replace('.oas', '.oas.txt'), 'w') as f:
                f.write(f"OAS Periodic Layout Description\n")
                f.write(f"Cell: {cell_name}\n")
                f.write(f"Repeat: X={repeat_x}, Y={repeat_y}\n")
                f.write(f"Pitch: X={params.pitch_x if params else 'N/A'}, ")
                f.write(f"Y={params.pitch_y if params else 'N/A'}\n\n")
                
                for i, feature in enumerate(features):
                    f.write(f"Unit Feature {i}: {feature.shape_type}\n")
                    f.write(f"  Vertices: {feature.vertices}\n\n")
            
            print(f"周期性OAS描述已保存 / Periodic OAS description saved")
    
    def _write_periodic_with_klayout(self, filename: str, features: List[GeometricFeature],
                                    params: LayoutParameters, repeat_x: int, repeat_y: int,
                                    cell_name: str) -> None:
        """使用klayout写入周期性OAS文件 / Write periodic OAS with klayout"""
        try:
            import pya
            
            layout = pya.Layout()
            
            # Create unit cell
            unit_cell = layout.create_cell(cell_name + "_UNIT")
            layer_idx = layout.layer(params.layer if params else 0,
                                    params.datatype if params else 0)
            
            for feature in features:
                points = [pya.Point(int(x * 1000), int(y * 1000))
                         for x, y in feature.vertices]
                poly = pya.Polygon(points)
                unit_cell.shapes(layer_idx).insert(poly)
            
            # Create main cell with array
            main_cell = layout.create_cell(cell_name)
            
            pitch_x = int((params.pitch_x if params and params.pitch_x else 100) * 1000)
            pitch_y = int((params.pitch_y if params and params.pitch_y else 100) * 1000)
            
            for i in range(repeat_x):
                for j in range(repeat_y):
                    trans = pya.Trans(pya.Point(i * pitch_x, j * pitch_y))
                    main_cell.insert(pya.CellInstArray(unit_cell.cell_index(), trans))
            
            layout.write(filename)
            print(f"周期性OAS文件已保存 / Periodic OAS file saved: {filename}")
            
        except Exception as e:
            print(f"写入失败: {e} / Write failed: {e}")
    
    def write_batch(self, base_filename: str, layouts: List[dict]) -> List[str]:
        """
        批量写入OAS文件
        Batch write OAS files
        
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
            
            filename = f"{base_filename}_{name}.oas"
            self.write(filename, features, params, name)
            filenames.append(filename)
        
        print(f"批量生成了 {len(filenames)} 个OAS文件 / Batch generated {len(filenames)} OAS files")
        return filenames
