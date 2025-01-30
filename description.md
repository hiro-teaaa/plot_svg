# Google Maps URLからSVGプロットまでの仕様説明

このドキュメントでは、Google Maps URLから座標を取得し、SVG上にプロットするまでの一連の処理について説明します。

## 1. 座標取得の仕組み

### 1.1 Google Maps URLの形式について
Google Maps URLには主に2つの形式があります：

1. クエリパラメータ形式（`q=`パラメータを使用）
```
https://www.google.com/maps/place?q=35.681236,139.767125
```

2. パス形式（ショートURL展開後、`@`を使用）
```
https://www.google.com/maps/@35.681236,139.767125,15z
```

### 1.2 座標抽出の処理
`map_utils.py`の`extract_lat_lng`関数では、以下のような処理を行います：

```python
def extract_lat_lng(google_maps_url):
    parsed_url = urlparse(google_maps_url)
    query_params = parse_qs(parsed_url.query)
    
    # クエリパラメータ形式の場合
    if 'q' in query_params:
        lat_lng_str = query_params['q'][0]  # "35.681236,139.767125"の形式
        lat_str, lng_str = lat_lng_str.split(',')
        return float(lat_str), float(lng_str)
    
    # パス形式の場合
    elif '@' in parsed_url.path:
        path_parts = parsed_url.path.split('@')[1].split(',')
        return float(path_parts[0]), float(path_parts[1])
```

## 2. SVG座標への変換処理

### 2.1 変換の基本的な考え方
緯度経度からSVG座標への変換では、以下の原則に基づいた線形変換を使用します：

1. 緯度からY座標への変換：
   - 北が上（Y座標が小さい値）、南が下（Y座標が大きい値）
   - 最北端の緯度がY=0に、最南端の緯度がY=heightに対応

2. 経度からX座標への変換：
   - 西が左（X座標が小さい値）、東が右（X座標が大きい値）
   - 最西端の経度がX=0に、最東端の経度がX=widthに対応

### 2.2 変換の実装
`map_utils.py`の`lat_lng_to_svg_coords`関数で、以下のように実装しています：

```python
def lat_lng_to_svg_coords(lat, lng, svg_width, svg_height, prefecture_id):
    # 都道府県の境界情報を取得
    min_lat, max_lat, min_lng, max_lng = get_prefecture_bounds(prefecture_id)
    
    # 座標が範囲内に収まっているかチェック
    if not (min_lat <= lat <= max_lat and min_lng <= lng <= max_lng):
        raise ValueError("指定された座標が都道府県の範囲外です")
    
    # 経度からX座標を計算
    x = (lng - min_lng) / (max_lng - min_lng) * svg_width
    
    # 緯度からY座標を計算（SVGは上が0なので反転）
    y = (max_lat - lat) / (max_lat - min_lat) * svg_height
    
    return x, y
```

## 3. SVG上へのプロット処理

### 3.1 フロントエンドでの表示方法
`index.html`では、サーバーから受け取った座標情報を使用して以下のようにマーカーを配置します。

#### 3.1.1 マーカー配置の仕組み
SVGとマーカーボタンの位置合わせは、以下の方法で実現しています：

1. コンテナの構造
```html
<div class="map-container" id="mapContainer">
    <!-- SVG要素 -->
    <svg class="map-svg">...</svg>
    <!-- マーカーボタン -->
    <button class="marker-button">...</button>
</div>
```

2. コンテナのスタイル設定
```css
.map-container {
    position: relative;  /* 子要素の絶対位置指定の基準点となる */
    width: 100%;
    max-width: 1000px;
    margin: 20px auto;
    overflow: hidden;   /* はみ出し防止 */
}

.map-svg {
    width: 100%;       /* コンテナいっぱいに表示 */
    height: auto;      /* アスペクト比を保持 */
    display: block;
}
```

3. 座標変換とマーカー配置
```javascript
// SVG座標をパーセンテージに変換
const percentX = (data.coordinates.x / data.coordinates.width) * 100;
const percentY = (data.coordinates.y / data.coordinates.height) * 100;

// マーカーの位置を設定
marker.style.left = `${percentX}%`;
marker.style.top = `${percentY}%`;
```

#### 3.1.2 位置合わせの詳細な仕組み

1. **相対位置指定の基準点**
   - `map-container`に`position: relative`を設定することで、この要素が子要素の位置指定の基準点となります
   - マーカーボタンは`position: absolute`で配置され、コンテナを基準とした位置に表示されます

2. **SVGのサイズ管理**
   - SVGは`width: 100%`で表示され、コンテナの幅いっぱいに広がります
   - `height: auto`により、SVGの元のアスペクト比が保持されます
   - これにより、画面サイズが変わってもSVGとマーカーの相対位置が維持されます

3. **マーカーの位置計算**
   - サーバーから受け取ったSVG座標（x, y）を、SVGの幅・高さに対する割合（パーセンテージ）に変換
   - このパーセンテージ値を使って、マーカーの`left`と`top`プロパティを設定
   - `transform: translate(-50%, -50%)`により、マーカーの中心が計算された座標に来るように調整

4. **レスポンシブ対応**
   - パーセンテージベースの配置により、画面サイズが変わってもSVGとマーカーの相対位置が保持されます
   - コンテナの`max-width`設定により、大画面での表示サイズを制限

## 4. デバッグ情報の出力

変換処理の各段階で、以下の情報を出力して確認できるようにしています：

1. 入力された座標（緯度・経度）
2. 対象となる地図の境界範囲
3. SVGのサイズ情報（幅・高さ）
4. 変換後のSVG座標（x, y）

出力例：
```json
{
    "input_coords": {
        "lat": 35.681236,
        "lng": 139.767125
    },
    "map_bounds": {
        "min_lat": 35.0,
        "max_lat": 36.0,
        "min_lng": 139.0,
        "max_lng": 140.0
    },
    "svg_size": {
        "width": 800,
        "height": 600
    },
    "output_coords": {
        "x": 400,
        "y": 300
    }
}
```

## 5. エラー処理

以下のような場合にエラー処理を行い、適切なメッセージをユーザーに表示します：

1. URLの形式が不正な場合
2. 指定された座標が都道府県の範囲外の場合
3. SVGファイルの読み込みに失敗した場合
4. 座標の変換処理に失敗した場合

各エラーは、具体的な原因と対処方法がわかるメッセージとともにユーザーに通知されます。 
