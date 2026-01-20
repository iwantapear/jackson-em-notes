# Layout Pattern Recognition and GDS/OAS Generation Tool

## 概述 (Overview)

本工具通过识别图形几何特征，将pattern转译为OAS或GDS版图文件。

This tool identifies geometric features from patterns and converts them to OAS or GDS layout files.

## 功能特性 (Features)

### 1. 几何特征识别 (Geometric Feature Detection)
- 识别矩形 (Rectangle detection)
- 识别三角形 (Triangle detection)
- 识别多边形 (Polygon detection)
- 识别曼哈顿版图几何特征 (Manhattan layout detection)

### 2. 周期性和对称性识别 (Periodicity and Symmetry Detection)
- X方向周期性检测 (X-direction periodicity)
- Y方向周期性检测 (Y-direction periodicity)
- XY双向周期性检测 (XY bidirectional periodicity)
- 最小周期单元提取 (Minimal period unit extraction)

### 3. 交互式参数定义 (Interactive Parameter Definition)
- 矩形尺寸 (Rectangle dimensions: length, width)
- 间距 (Gap spacing)
- XY方向pitch (XY pitch values)
- 关键尺寸CD (Critical Dimension)

### 4. 批量生成 (Batch Generation)
- 通过pitch范围设定批量生成不同参数的版图
- Batch generation of layouts with different parameters via pitch ranges

### 5. 文件生成 (File Generation)
- GDS格式输出 (GDS format output)
- OAS格式输出 (OAS format output)
- Patch配置文件 (Patch configuration files)
- Gauge (CW) 配置文件 (Gauge configuration files)

### 6. 非周期性版图支持 (Non-periodic Layout Support)
- 周期延拓配置 (Periodic extension configuration)

## 安装 (Installation)

```bash
# Install required dependencies
pip install -r requirements.txt
```

## 使用方法 (Usage)

### 基本用法 (Basic Usage)

```python
from layout_tool import LayoutRecognizer, GDSWriter, OASWriter

# 1. Load and analyze pattern
recognizer = LayoutRecognizer()
pattern = recognizer.load_image("pattern.png")

# 2. Detect geometric features
features = recognizer.detect_features(pattern)

# 3. Detect periodicity
periodicity = recognizer.detect_periodicity(features)

# 4. Define parameters interactively
params = recognizer.interactive_parameter_definition(features)

# 5. Generate GDS file
gds_writer = GDSWriter()
gds_writer.write("output.gds", features, params)

# 6. Generate OAS file
oas_writer = OASWriter()
oas_writer.write("output.oas", features, params)
```

### 批量生成 (Batch Generation)

```python
# Generate batch layouts with varying pitch
batch_params = {
    'pitch_x_range': (100, 500, 50),  # start, end, step
    'pitch_y_range': (100, 500, 50),
}

layouts = recognizer.batch_generate(features, batch_params)
for i, layout in enumerate(layouts):
    gds_writer.write(f"output_{i}.gds", layout.features, layout.params)
```

### 配置文件生成 (Configuration File Generation)

```python
from config_generator import PatchConfigGenerator, GaugeConfigGenerator

# Generate patch configuration
patch_gen = PatchConfigGenerator()
patch_gen.generate("patch_config.yaml", features, params)

# Generate gauge (CW) configuration
gauge_gen = GaugeConfigGenerator()
gauge_gen.generate("gauge_config.cw", features, params)
```

## 示例 (Examples)

详见 `examples/` 目录中的示例文件。
See example files in the `examples/` directory.

## 技术实现 (Technical Implementation)

- **图像处理**: OpenCV + scikit-image
- **几何分析**: Shapely
- **GDS/OAS生成**: gdspy / python-gdsii
- **交互界面**: Tkinter / Qt
- **配置文件**: YAML / JSON

## 局限性 (Limitations)

- 图像质量会影响识别准确度
- 复杂图形可能需要手动调整参数
- 非常规形状可能需要额外配置

## 贡献 (Contributing)

欢迎提交问题和改进建议！
Issues and improvements are welcome!

## 许可证 (License)

与主仓库保持一致
Same as the main repository
