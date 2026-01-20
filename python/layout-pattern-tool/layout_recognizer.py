"""
Layout Pattern Recognizer Module

识别图形几何特征的核心模块
Core module for recognizing geometric features from patterns
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

# Optional imports for image processing
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("Warning: OpenCV not installed. Image loading functionality will be limited.")

try:
    from shapely.geometry import Polygon, box
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False

try:
    from scipy import ndimage
    from scipy.signal import find_peaks
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@dataclass
class GeometricFeature:
    """几何特征数据类 / Geometric feature data class"""
    shape_type: str  # 'rectangle', 'triangle', 'polygon', 'manhattan'
    vertices: List[Tuple[float, float]]
    centroid: Tuple[float, float]
    area: float
    perimeter: float
    bounding_box: Tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max)
    properties: Dict[str, Any] = None


@dataclass
class PeriodicityInfo:
    """周期性信息数据类 / Periodicity information data class"""
    has_x_periodicity: bool
    has_y_periodicity: bool
    x_period: Optional[float]
    y_period: Optional[float]
    minimal_unit: Optional[GeometricFeature]
    repeat_count_x: int
    repeat_count_y: int


@dataclass
class LayoutParameters:
    """版图参数数据类 / Layout parameters data class"""
    width: Optional[float] = None
    height: Optional[float] = None
    gap_x: Optional[float] = None
    gap_y: Optional[float] = None
    pitch_x: Optional[float] = None
    pitch_y: Optional[float] = None
    cd: Optional[float] = None  # Critical Dimension
    layer: int = 0
    datatype: int = 0
    custom_params: Dict[str, Any] = None


class LayoutRecognizer:
    """
    版图识别器主类
    Main class for layout pattern recognition
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化识别器
        Initialize the recognizer
        
        Args:
            config: 配置参数字典 / Configuration dictionary
        """
        self.config = config or {}
        self.image = None
        self.processed_image = None
        self.features: List[GeometricFeature] = []
        
    def load_image(self, image_path: str) -> np.ndarray:
        """
        加载图像文件
        Load image file
        
        Args:
            image_path: 图像文件路径 / Image file path
            
        Returns:
            加载的图像数组 / Loaded image array
        """
        if not HAS_CV2:
            raise ImportError("OpenCV (cv2) is required for image loading. Install with: pip install opencv-python")
        
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"无法加载图像: {image_path} / Cannot load image: {image_path}")
        
        # Convert to grayscale for processing
        self.processed_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return self.image
    
    def detect_features(self, image: Optional[np.ndarray] = None) -> List[GeometricFeature]:
        """
        检测几何特征
        Detect geometric features
        
        Args:
            image: 可选的输入图像 / Optional input image
            
        Returns:
            检测到的几何特征列表 / List of detected geometric features
        """
        if not HAS_CV2:
            raise ImportError("OpenCV (cv2) is required for feature detection. Install with: pip install opencv-python")
        
        if image is not None:
            self.processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        if self.processed_image is None:
            raise ValueError("没有可用的图像进行处理 / No image available for processing")
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(self.processed_image, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        self.features = []
        for contour in contours:
            if cv2.contourArea(contour) < 100:  # Filter small noise
                continue
            
            feature = self._analyze_contour(contour)
            if feature:
                self.features.append(feature)
        
        return self.features
    
    def _analyze_contour(self, contour) -> Optional[GeometricFeature]:
        """
        分析轮廓并识别形状
        Analyze contour and identify shape
        """
        if not HAS_CV2:
            return None
            
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Get properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        M = cv2.moments(contour)
        
        if M["m00"] == 0:
            return None
        
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        
        # Extract vertices
        vertices = [(float(pt[0][0]), float(pt[0][1])) for pt in approx]
        
        # Determine shape type
        num_vertices = len(approx)
        shape_type = 'polygon'
        
        if num_vertices == 3:
            shape_type = 'triangle'
        elif num_vertices == 4:
            # Check if it's a rectangle
            if self._is_rectangle(approx):
                shape_type = 'rectangle'
            # Check if it's Manhattan (right angles)
            elif self._is_manhattan(approx):
                shape_type = 'manhattan'
        elif self._is_manhattan_polygon(approx):
            shape_type = 'manhattan'
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        bounding_box = (float(x), float(y), float(x + w), float(y + h))
        
        properties = {
            'num_vertices': num_vertices,
            'aspect_ratio': w / h if h > 0 else 0,
        }
        
        return GeometricFeature(
            shape_type=shape_type,
            vertices=vertices,
            centroid=(cx, cy),
            area=area,
            perimeter=perimeter,
            bounding_box=bounding_box,
            properties=properties
        )
    
    def _is_rectangle(self, approx) -> bool:
        """检查是否为矩形 / Check if shape is a rectangle"""
        if len(approx) != 4:
            return False
        
        # Check if all angles are approximately 90 degrees
        angles = []
        for i in range(4):
            p1 = approx[i][0]
            p2 = approx[(i + 1) % 4][0]
            p3 = approx[(i + 2) % 4][0]
            
            v1 = p1 - p2
            v2 = p3 - p2
            
            angle = np.abs(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            angles.append(angle)
        
        # All angles should be close to 90 degrees (cosine close to 0)
        return all(angle < 0.1 for angle in angles)
    
    def _is_manhattan(self, approx) -> bool:
        """检查是否为曼哈顿几何 / Check if shape is Manhattan geometry"""
        # Manhattan geometry has edges aligned with X or Y axis
        for i in range(len(approx)):
            p1 = approx[i][0]
            p2 = approx[(i + 1) % len(approx)][0]
            
            dx = abs(p2[0] - p1[0])
            dy = abs(p2[1] - p1[1])
            
            # Edge should be either horizontal or vertical
            if dx > 1 and dy > 1:  # Allow small tolerance
                return False
        
        return True
    
    def _is_manhattan_polygon(self, approx) -> bool:
        """检查多边形是否为曼哈顿几何 / Check if polygon is Manhattan geometry"""
        return self._is_manhattan(approx)
    
    def detect_periodicity(self, features: Optional[List[GeometricFeature]] = None) -> PeriodicityInfo:
        """
        检测周期性和对称性
        Detect periodicity and symmetry
        
        Args:
            features: 几何特征列表 / List of geometric features
            
        Returns:
            周期性信息 / Periodicity information
        """
        if features is None:
            features = self.features
        
        if len(features) < 2:
            return PeriodicityInfo(
                has_x_periodicity=False,
                has_y_periodicity=False,
                x_period=None,
                y_period=None,
                minimal_unit=None,
                repeat_count_x=1,
                repeat_count_y=1
            )
        
        # Extract centroids
        centroids = np.array([f.centroid for f in features])
        
        # Detect X-direction periodicity
        x_coords = sorted(centroids[:, 0])
        x_diffs = np.diff(x_coords)
        x_period, x_count = self._detect_period(x_diffs)
        
        # Detect Y-direction periodicity
        y_coords = sorted(centroids[:, 1])
        y_diffs = np.diff(y_coords)
        y_period, y_count = self._detect_period(y_diffs)
        
        # Find minimal unit (first feature, can be improved)
        minimal_unit = features[0] if features else None
        
        return PeriodicityInfo(
            has_x_periodicity=x_period is not None,
            has_y_periodicity=y_period is not None,
            x_period=x_period,
            y_period=y_period,
            minimal_unit=minimal_unit,
            repeat_count_x=x_count,
            repeat_count_y=y_count
        )
    
    def _detect_period(self, diffs: np.ndarray, tolerance: float = 0.1) -> Tuple[Optional[float], int]:
        """
        从间距数组中检测周期
        Detect period from spacing array
        
        Args:
            diffs: 间距数组 / Array of spacings
            tolerance: 容差比例 / Tolerance ratio
            
        Returns:
            (周期值, 重复次数) / (period value, repeat count)
        """
        if len(diffs) == 0:
            return None, 1
        
        # Find most common spacing (within tolerance)
        mean_diff = np.mean(diffs)
        mask = np.abs(diffs - mean_diff) < mean_diff * tolerance
        
        if np.sum(mask) >= len(diffs) * 0.7:  # At least 70% of spacings are similar
            period = np.mean(diffs[mask])
            count = np.sum(mask) + 1
            return period, count
        
        return None, 1
    
    def interactive_parameter_definition(self, features: Optional[List[GeometricFeature]] = None) -> LayoutParameters:
        """
        交互式参数定义
        Interactive parameter definition
        
        Args:
            features: 几何特征列表 / List of geometric features
            
        Returns:
            版图参数 / Layout parameters
        """
        if features is None:
            features = self.features
        
        params = LayoutParameters()
        
        print("=" * 60)
        print("交互式参数定义 / Interactive Parameter Definition")
        print("=" * 60)
        
        # For simplicity, provide default values based on detected features
        if features:
            first_feature = features[0]
            bbox = first_feature.bounding_box
            params.width = bbox[2] - bbox[0]
            params.height = bbox[3] - bbox[1]
            
            print(f"检测到的宽度 / Detected width: {params.width:.2f}")
            print(f"检测到的高度 / Detected height: {params.height:.2f}")
        
        # Detect spacing if multiple features
        if len(features) >= 2:
            centroids = [f.centroid for f in features]
            x_gaps = []
            y_gaps = []
            
            for i in range(len(centroids) - 1):
                x_gaps.append(abs(centroids[i + 1][0] - centroids[i][0]))
                y_gaps.append(abs(centroids[i + 1][1] - centroids[i][1]))
            
            if x_gaps:
                params.gap_x = min([g for g in x_gaps if g > 0], default=None)
                params.pitch_x = np.mean(x_gaps) if x_gaps else None
                gap_x_str = f"{params.gap_x:.2f}" if params.gap_x else "N/A"
                pitch_x_str = f"{params.pitch_x:.2f}" if params.pitch_x else "N/A"
                print(f"检测到的X方向间距 / Detected X gap: {gap_x_str}")
                print(f"检测到的X方向pitch / Detected X pitch: {pitch_x_str}")
            
            if y_gaps:
                params.gap_y = min([g for g in y_gaps if g > 0], default=None)
                params.pitch_y = np.mean(y_gaps) if y_gaps else None
                gap_y_str = f"{params.gap_y:.2f}" if params.gap_y else "N/A"
                pitch_y_str = f"{params.pitch_y:.2f}" if params.pitch_y else "N/A"
                print(f"检测到的Y方向间距 / Detected Y gap: {gap_y_str}")
                print(f"检测到的Y方向pitch / Detected Y pitch: {pitch_y_str}")
        
        # CD (Critical Dimension) - typically minimum feature size
        if features:
            min_dim = min([min(f.bounding_box[2] - f.bounding_box[0], 
                              f.bounding_box[3] - f.bounding_box[1]) for f in features])
            params.cd = min_dim
            print(f"检测到的关键尺寸CD / Detected CD: {params.cd:.2f}")
        
        print("=" * 60)
        print("提示: 在实际应用中，可以通过GUI界面手动调整这些参数")
        print("Tip: In actual application, these parameters can be adjusted via GUI")
        print("=" * 60)
        
        return params
    
    def batch_generate(self, features: List[GeometricFeature], 
                      batch_params: Dict[str, Tuple[float, float, float]]) -> List[Dict]:
        """
        批量生成不同参数的版图
        Batch generate layouts with varying parameters
        
        Args:
            features: 几何特征列表 / List of geometric features
            batch_params: 批量参数范围 / Batch parameter ranges
                         格式 / Format: {'pitch_x_range': (start, end, step), ...}
        
        Returns:
            生成的版图列表 / List of generated layouts
        """
        layouts = []
        
        # Extract ranges
        pitch_x_range = batch_params.get('pitch_x_range', (100, 100, 100))
        pitch_y_range = batch_params.get('pitch_y_range', (100, 100, 100))
        
        # Generate all combinations
        x_values = np.arange(pitch_x_range[0], pitch_x_range[1] + pitch_x_range[2], pitch_x_range[2])
        y_values = np.arange(pitch_y_range[0], pitch_y_range[1] + pitch_y_range[2], pitch_y_range[2])
        
        for pitch_x in x_values:
            for pitch_y in y_values:
                params = LayoutParameters(
                    pitch_x=pitch_x,
                    pitch_y=pitch_y,
                )
                
                layout = {
                    'features': features,
                    'params': params,
                    'name': f'layout_px{pitch_x:.0f}_py{pitch_y:.0f}'
                }
                layouts.append(layout)
        
        print(f"生成了 {len(layouts)} 个版图 / Generated {len(layouts)} layouts")
        return layouts
