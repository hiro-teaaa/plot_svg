"""
緯度経度から都道府県を判定するモジュール
"""
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional
import cairo
import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg  # rsvgの代わりにこちらを使用
from config.prefecture_configs import PREFECTURE_CONFIGS
from utils.map_utils import lat_lng_to_svg_coords

def get_svg_path_data(prefecture_id: str) -> str:
    """
    都道府県のSVGファイルからパスデータを取得
    
    Args:
        prefecture_id: 都道府県ID
        
    Returns:
        str: SVGのパスデータ（d属性の値）
    """
    svg_file = f"static/maps/{PREFECTURE_CONFIGS[prefecture_id]['svg_file']}"
    tree = ET.parse(svg_file)
    root = tree.getroot()
    path = root.find(".//{http://www.w3.org/2000/svg}path")
    return path.get('d')

def is_point_in_svg_path(x: float, y: float, svg_file: str) -> bool:
    """
    SVG上の点が塗りつぶされているかを判定
    """
    # Rsvgハンドラーを使用
    handle = Rsvg.Handle.new_from_file(svg_file)
    dim = handle.get_dimensions()
    
    # サーフェスの作成
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 
                               dim.width,
                               dim.height)
    context = cairo.Context(surface)
    
    # SVGをレンダリング
    handle.render_cairo(context)
    
    # 座標チェック
    x, y = int(x), int(y)
    if x < 0 or y < 0 or x >= dim.width or y >= dim.height:
        return False
        
    # ピクセルデータを取得
    pixel = surface.get_data()[y * surface.get_stride() + x * 4:
                              y * surface.get_stride() + (x + 1) * 4]
    
    return pixel[3] > 0  # アルファ値をチェック

def get_prefecture_candidates(lat: float, lng: float) -> List[str]:
    """
    緯度経度から候補となる都道府県のリストを取得
    
    Args:
        lat: 緯度
        lng: 経度
        
    Returns:
        List[str]: 候補となる都道府県IDのリスト（都道府県コード順）
    """
    candidates = []
    for pref_id, config in PREFECTURE_CONFIGS.items():
        bounds = config['bounds']
        if (bounds['min_lat'] <= lat <= bounds['max_lat'] and
            bounds['min_lng'] <= lng <= bounds['max_lng']):
            candidates.append(pref_id)
    
    # 都道府県コード順にソート
    return sorted(candidates, key=lambda x: PREFECTURE_CONFIGS[x]['code'])

def detect_prefecture(lat: float, lng: float) -> Tuple[str, dict]:
    """
    緯度経度から都道府県を判定
    
    Args:
        lat: 緯度
        lng: 経度
        
    Returns:
        Tuple[str, dict]: (都道府県ID, デバッグ情報)
        
    Raises:
        ValueError: 判定できない場合
    """
    # 1. 候補を取得（都道府県コード順）
    candidates = get_prefecture_candidates(lat, lng)
    if not candidates:
        raise ValueError("指定された緯度経度は日本の都道府県の範囲外です。")
    
    debug_info = {
        'input_coords': {'lat': lat, 'lng': lng},
        'candidates': candidates
    }
    
    # 2. 各候補についてSVG判定
    for pref_id in candidates:
        config = PREFECTURE_CONFIGS[pref_id]
        
        # 緯度経度をSVG座標に変換
        try:
            x, y = lat_lng_to_svg_coords(
                lat, lng,
                config['default_width'],
                config['default_height'],
                pref_id
            )
        except ValueError:
            continue
        
        # SVGファイルで判定
        svg_file = f"static/maps/{config['svg_file']}"
        if is_point_in_svg_path(x, y, svg_file):
            debug_info['selected_prefecture'] = {
                'id': pref_id,
                'name': config['name'],
                'svg_coords': {'x': x, 'y': y}
            }
            return pref_id, debug_info
    
    raise ValueError("指定された地点の都道府県を判定できませんでした。") 