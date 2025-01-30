"""
都道府県ごとの地図設定を管理するモジュール
"""

PREFECTURE_CONFIGS = {
    'aomori': {
        'name': '青森県',
        'code': 2,  # 都道府県コード
        'bounds': {
            'min_lat': 40.218,  # 40°13'04"
            'max_lat': 41.556,  # 41°33'22"
            'min_lng': 139.497, # 139°29'49"
            'max_lng': 141.683  # 141°41'00"
        },
        'svg_file': 'aomori.svg',  # static/maps/内のファイル名
        'default_width': 2107,      # SVGのviewBox幅に合わせる
        'default_height': 2044      # SVGのviewBox高さに合わせる
    },
    'iwate': {
        'name': '岩手県',
        'code': 3,
        'bounds': {
            'min_lat': 38.748,  # 38°44'52"
            'max_lat': 40.450,  # 40°27'02"
            'min_lng': 140.653, # 140°39'11"
            'max_lng': 142.073  # 142°04'21"
        },
        'svg_file': 'iwate.svg',
        'default_width': 1641,
        'default_height': 2538
    },
    'miyagi': {
        'name': '宮城県',
        'code': 4,
        'bounds': {
            'min_lat': 37.773,  # 37°46'24"
            'max_lat': 39.003,  # 39°00'10"
            'min_lng': 140.275, # 140°16'30"
            'max_lng': 141.677  # 141°40'38"
        },
        'svg_file': 'miyagi.svg',
        'default_width': 1630,
        'default_height': 1803
    },
    'akita': {
        'name': '秋田県',
        'code': 5,
        'bounds': {
            'min_lat': 38.873,  # 38°52'23"
            'max_lat': 40.511,  # 40°30'40"
            'min_lng': 139.692, # 139°41'30"
            'max_lng': 140.995  # 140°59'43"
        },
        'svg_file': 'akita.svg',
        'default_width': 1475,
        'default_height': 2443
    },
    'yamagata': {
        'name': '山形県',
        'code': 6,
        'bounds': {
            'min_lat': 37.734,  # 37°44'02"
            'max_lat': 39.216,  # 39°12'56"
            'min_lng': 139.520, # 139°31'12"
            'max_lng': 140.647  # 140°38'48"
        },
        'svg_file': 'yamagata.svg',
        'default_width': 1252,
        'default_height': 2054
    },
    'fukushima': {
        'name': '福島県',
        'code': 7,
        'bounds': {
            'min_lat': 36.791,  # 36°47'29"
            'max_lat': 37.977,  # 37°58'36"
            'min_lng': 139.165, # 139°09'53"
            'max_lng': 141.044  # 141°02'37"
        },
        'svg_file': 'fukushima.svg',
        'default_width': 2178,
        'default_height': 1711
    }
} 
