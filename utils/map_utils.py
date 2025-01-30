import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import os
from config.prefecture_configs import PREFECTURE_CONFIGS

def expand_url(short_url):
    """
    短縮URLを展開して通常URLを返す。
    """
    response = requests.head(short_url, allow_redirects=True)
    return response.url

def extract_lat_lng(google_maps_url):
    """
    Google MapsのURLから緯度経度を抽出。
    'q=35.xxx,139.xxx' または '/@35.xxx,139.xxx,' の形式に対応。
    """
    parsed_url = urlparse(google_maps_url)
    query_params = parse_qs(parsed_url.query)
    
    if 'q' in query_params:
        lat_lng_str = query_params['q'][0]  # 例 "35.xxx,139.xxx"
        lat_str, lng_str = lat_lng_str.split(',')
        return float(lat_str), float(lng_str)
    elif '@' in parsed_url.path:
        # pathが "/@35.xxx,139.xxx,17z" などの形式を想定
        path_parts = parsed_url.path.split('@')[1].split(',')
        return float(path_parts[0]), float(path_parts[1])
    else:
        raise ValueError("緯度・経度情報がURLから取得できませんでした。")

def get_prefecture_bounds(prefecture_id):
    """
    都道府県の地図境界情報を取得
    """
    if prefecture_id not in PREFECTURE_CONFIGS:
        raise ValueError(f"都道府県ID '{prefecture_id}' が見つかりません。")
    
    bounds = PREFECTURE_CONFIGS[prefecture_id]['bounds']
    return (
        bounds['min_lat'],
        bounds['max_lat'],
        bounds['min_lng'],
        bounds['max_lng']
    )

def lat_lng_to_svg_coords(lat, lng, svg_width, svg_height, prefecture_id):
    """
    線形変換で (lat, lng) → (x, y) を求める。
    prefecture_idに基づいて適切な境界値を使用。
    """
    min_lat, max_lat, min_lng, max_lng = get_prefecture_bounds(prefecture_id)
    
    # デバッグ情報を出力
    print(f"\n=== 座標変換デバッグ情報 ===")
    print(f"入力座標: 緯度={lat}, 経度={lng}")
    print(f"地図範囲: 緯度={min_lat}～{max_lat}, 経度={min_lng}～{max_lng}")
    print(f"SVGサイズ: 幅={svg_width}, 高さ={svg_height}")
    
    # 座標が範囲内かチェック
    if not (min_lat <= lat <= max_lat and min_lng <= lng <= max_lng):
        raise ValueError(f"指定された座標が都道府県の範囲外です。\n"
                        f"許容範囲: 緯度={min_lat}～{max_lat}, 経度={min_lng}～{max_lng}\n"
                        f"入力値: 緯度={lat}, 経度={lng}")
    
    x = (lng - min_lng) / (max_lng - min_lng) * svg_width
    y = (max_lat - lat) / (max_lat - min_lat) * svg_height
    
    print(f"変換後のSVG座標: x={x:.1f}, y={y:.1f}")
    print("========================\n")
    
    return x, y

def load_base_svg(prefecture_id):
    """
    都道府県のベースとなるSVGファイルを読み込む
    """
    if prefecture_id not in PREFECTURE_CONFIGS:
        raise ValueError(f"都道府県ID '{prefecture_id}' が見つかりません。")
    
    config = PREFECTURE_CONFIGS[prefecture_id]
    svg_path = os.path.join('static', 'maps', config['svg_file'])
    
    if not os.path.exists(svg_path):
        raise FileNotFoundError(f"SVGファイル '{svg_path}' が見つかりません。")
    
    print(f"\nSVGファイル '{svg_path}' を読み込みます。")
    
    with open(svg_path, 'r', encoding='utf-8') as f:
        return f.read()

# マーカーをSVGに直接打つ場合
def create_svg_marker(x, y, prefecture_id):
    """
    ベースSVGを読み込み、マーカーを追加したSVGを返す
    """
    # ベースSVGを読み込む
    base_svg = load_base_svg(prefecture_id)
    print("\n=== ベースSVGの内容 ===")
    print(base_svg[:200] + "...")  # 最初の200文字だけ表示
    
    # SVGのルート要素を取得
    svg = ET.fromstring(base_svg)
    
    # viewBox属性を取得または設定
    viewBox = svg.get('viewBox')
    if not viewBox:
        # viewBoxが設定されていない場合は、width/heightから設定
        width = float(svg.get('width', '0'))
        height = float(svg.get('height', '0'))
        svg.set('viewBox', f'0 0 {width} {height}')
    
    # マーカーグループを作成（最前面に表示）
    marker_group = ET.SubElement(svg, 'g', {
        'class': 'marker',
        'style': 'pointer-events: none;'  # マーカーをクリック不可に
    })
    
    # 外側の円（白い縁取り）
    outer_circle = ET.SubElement(marker_group, 'circle', {
        'cx': str(x),
        'cy': str(y),
        'r': '15',  # サイズを大きく
        'fill': 'white',
        'stroke': 'none'
    })
    
    # 内側の円（赤）
    inner_circle = ET.SubElement(marker_group, 'circle', {
        'cx': str(x),
        'cy': str(y),
        'r': '10',  # サイズを大きく
        'fill': 'red',
        'stroke': 'none'
    })
    
    print(f"マーカーを追加: x={x:.1f}, y={y:.1f}, r=10（内側）/15（外側）")
    print(f"SVG viewBox: {svg.get('viewBox')}")
    
    # 生成されるSVGの内容を確認
    result_svg = ET.tostring(svg, encoding='unicode')
    print("\n=== 生成されるSVGの内容 ===")
    print(result_svg[:200] + "...")  # 最初の200文字だけ表示
    
    return result_svg 