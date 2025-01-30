from flask import Flask, request, render_template, Response, jsonify
from utils.map_utils import (
    expand_url, extract_lat_lng,
    lat_lng_to_svg_coords, load_base_svg
)
from config.prefecture_configs import PREFECTURE_CONFIGS

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """
    トップページ: Google Maps URL入力フォームを表示
    """
    # 都道府県の一覧を渡す
    prefectures = {
        id: config['name']
        for id, config in PREFECTURE_CONFIGS.items()
    }
    return render_template('index.html', prefectures=prefectures)

@app.route('/create-svg', methods=['POST'])
def create_svg():
    """
    フォーム送信されたURLを受け取り、SVGと座標情報を返す
    """
    google_maps_url = request.form.get('maps_url')
    prefecture_id = request.form.get('prefecture')
    
    print(f"\n=== SVG生成プロセス開始 ===")
    print(f"Google Maps URL: {google_maps_url}")
    print(f"選択された都道府県: {prefecture_id}")
    
    if not google_maps_url:
        return "URLが入力されていません。", 400
    if not prefecture_id:
        return "都道府県が選択されていません。", 400
    if prefecture_id not in PREFECTURE_CONFIGS:
        return "無効な都道府県が選択されました。", 400

    try:
        # 1) URL展開
        final_url = expand_url(google_maps_url)
        print(f"展開後のURL: {final_url}")
        
        # 2) 緯度経度抽出
        lat, lng = extract_lat_lng(final_url)
        print(f"抽出された座標: 緯度={lat}, 経度={lng}")
        
        # 3) SVG座標変換
        config = PREFECTURE_CONFIGS[prefecture_id]
        svg_width = float(config['default_width'])
        svg_height = float(config['default_height'])
        print(f"SVGサイズ設定: 幅={svg_width}, 高さ={svg_height}")
        
        try:
            x, y = lat_lng_to_svg_coords(lat, lng, svg_width, svg_height, prefecture_id)
        except ValueError as e:
            print(f"座標変換エラー: {str(e)}")
            return str(e), 400
        
        # 4) ベースSVGを読み込む
        base_svg = load_base_svg(prefecture_id)
        
        # デバッグ情報を作成
        debug_info = {
            'input_coords': {
                'lat': lat,
                'lng': lng
            },
            'map_bounds': {
                'min_lat': config['bounds']['min_lat'],
                'max_lat': config['bounds']['max_lat'],
                'min_lng': config['bounds']['min_lng'],
                'max_lng': config['bounds']['max_lng']
            },
            'svg_size': {
                'width': svg_width,
                'height': svg_height
            },
            'output_coords': {
                'x': x,
                'y': y
            }
        }
        
        # 5) 結果を返却
        return jsonify({
            'svg': base_svg,
            'coordinates': {
                'x': x,
                'y': y,
                'width': svg_width,
                'height': svg_height
            },
            'debug_info': debug_info
        })

    except Exception as e:
        print(f"エラーが発生: {str(e)}")
        return f"エラーが発生しました: {str(e)}", 400

if __name__ == '__main__':
    # Flaskアプリ起動
    app.run(debug=True) 