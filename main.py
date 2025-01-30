from flask import Flask, request, render_template, Response, jsonify
from utils.map_utils import (
    expand_url, extract_lat_lng,
    lat_lng_to_svg_coords, load_base_svg
)
from config.prefecture_configs import PREFECTURE_CONFIGS
from utils.prefecture_detector import detect_prefecture, get_prefecture_candidates

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """
    トップページ: Google Maps URL入力フォームを表示
    """
    return render_template('index.html')

@app.route('/create-svg', methods=['POST'])
def create_svg():
    """
    フォーム送信されたURLを受け取り、SVGと座標情報を返す
    """
    google_maps_url = request.form.get('maps_url')
    if not google_maps_url:
        return "URLが入力されていません。", 400

    try:
        # 1) URL展開
        final_url = expand_url(google_maps_url)
        
        # 2) 緯度経度抽出
        lat, lng = extract_lat_lng(final_url)
        
        # 3) 都道府県の候補を取得
        candidates = get_prefecture_candidates(lat, lng)
        candidate_info = [
            {
                'id': pref_id,
                'name': PREFECTURE_CONFIGS[pref_id]['name'],
                'code': PREFECTURE_CONFIGS[pref_id]['code']
            }
            for pref_id in candidates
        ]
        
        # 4) 都道府県の自動判定
        try:
            prefecture_id, debug_info = detect_prefecture(lat, lng)
        except ValueError as e:
            return str(e), 400
            
        # 5) SVG座標変換
        config = PREFECTURE_CONFIGS[prefecture_id]
        svg_width = float(config['default_width'])
        svg_height = float(config['default_height'])
        
        x, y = lat_lng_to_svg_coords(lat, lng, svg_width, svg_height, prefecture_id)
        
        # 6) ベースSVGを読み込む
        base_svg = load_base_svg(prefecture_id)
        
        # デバッグ情報に候補県リストを追加
        debug_info['candidate_prefectures'] = candidate_info
        
        # 7) 結果を返却
        return jsonify({
            'svg': base_svg,
            'coordinates': {
                'x': x,
                'y': y,
                'width': svg_width,
                'height': svg_height
            },
            'prefecture': {
                'id': prefecture_id,
                'name': config['name'],
                'code': config['code']
            },
            'debug_info': debug_info
        })

    except Exception as e:
        return f"エラーが発生しました: {str(e)}", 400

if __name__ == '__main__':
    # Flaskアプリ起動
    #  app.run(debug=True) 
    app.run(host='0.0.0.0', port=8080, debug=True) 