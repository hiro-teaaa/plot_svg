"""
都道府県ごとの地図設定を管理するモジュール
"""

PREFECTURE_CONFIGS = {
    'aomori': {
        'name': '青森県',
        'code': 2,  # 都道府県コード
        'bounds': {
            'min_lat': 40.2,  # 最南端の緯度
            'max_lat': 41.6,  # 最北端の緯度
            'min_lng': 139.5, # 最西端の経度
            'max_lng': 141.6  # 最東端の経度
        },
        'svg_file': 'aomori.svg',  # static/maps/内のファイル名
        'default_width': 2107,      # SVGのviewBox幅に合わせる
        'default_height': 2044      # SVGのviewBox高さに合わせる
    }
} 
