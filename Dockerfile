FROM python:3.11-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# アプリケーションのコピー
COPY . .

# 実行時の設定
ENV FLASK_APP=main.py
ENV FLASK_DEBUG=0

# ポートの設定
EXPOSE 8080

# 起動コマンド（ログレベルをwarningに設定）
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "--log-level", "warning", "main:app"] 