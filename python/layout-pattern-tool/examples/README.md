# 使用示例 / Usage Examples

本目录包含了版图模式识别和GDS/OAS生成工具的使用示例。
This directory contains usage examples for the layout pattern recognition and GDS/OAS generation tool.

## 示例列表 / Examples List

### 示例 1: 基本几何特征识别和GDS生成
### Example 1: Basic Geometric Feature Detection and GDS Generation

文件: `example1_basic.py`

演示:
- 创建简单的矩形阵列图案
- 检测几何特征
- 检测周期性
- 生成GDS和OAS文件
- 生成Patch和Gauge配置文件

运行:
```bash
python example1_basic.py
```

### 示例 2: 批量生成不同pitch参数的版图
### Example 2: Batch Generation with Varying Pitch Parameters

文件: `example2_batch.py`

演示:
- 定义基础图案
- 设置pitch参数范围
- 批量生成多个版图
- 批量导出GDS文件

运行:
```bash
python example2_batch.py
```

### 示例 3: 非周期性版图的周期延拓
### Example 3: Periodic Extension for Non-periodic Layouts

文件: `example3_extension.py`

演示:
- 创建非周期性图案
- 检测周期性（确认无周期性）
- 设置周期延拓参数
- 生成周期延拓配置文件

运行:
```bash
python example3_extension.py
```

## 生成的文件 / Generated Files

运行示例后，将在本目录下生成以下文件:

### GDS文件:
- `example1_basic.gds` - 基本矩形阵列版图
- `example1_periodic.gds` - 周期性版图
- `batch_*.gds` - 批量生成的版图文件

### OAS文件:
- `example1_basic.oas` (或 `.oas.txt`) - OAS格式版图

### 配置文件:
- `example1_patch.yaml` - Patch配置
- `example1_gauge.cw` - Gauge配置
- `example3_extension.yaml` - 周期延拓配置

## 注意事项 / Notes

1. 运行示例前需要安装依赖包:
   ```bash
   pip install -r ../requirements.txt
   ```

2. 如果没有安装klayout，OAS文件将以文本格式保存

3. 所有示例都使用程序生成的测试图案，实际使用时可以从图像文件加载

## 实际图像识别示例 / Real Image Recognition Example

如果您有实际的图像文件，可以这样使用:

```python
from layout_tool import LayoutRecognizer, GDSWriter

# 加载图像
recognizer = LayoutRecognizer()
image = recognizer.load_image("your_pattern.png")

# 检测特征
features = recognizer.detect_features(image)

# 检测周期性
periodicity = recognizer.detect_periodicity(features)

# 交互式定义参数
params = recognizer.interactive_parameter_definition(features)

# 生成GDS
gds_writer = GDSWriter()
gds_writer.write("output.gds", features, params)
```
