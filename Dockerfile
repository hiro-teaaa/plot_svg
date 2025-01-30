FROM python:3.9-slim

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libgirepository1.0-dev \
    pkg-config \
    python3-dev \
    gir1.2-rsvg-2.0 \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pythonパッケージの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# ポート8080を公開
EXPOSE 8080

# Flaskアプリケーションを実行
CMD ["python", "main.py"] 