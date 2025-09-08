#!/usr/bin/env python3
"""
Template Image Creator セットアップスクリプト
"""

import os
import sys

def create_directories():
    """必要なディレクトリを作成"""
    directories = ['img', 'templates', 'fonts']
    
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ {dir_name}/ フォルダを作成しました")
        else:
            print(f"📁 {dir_name}/ フォルダは既に存在します")

def create_env_file():
    """環境変数ファイルのサンプルを作成"""
    env_content = """# Figma API設定
FIGMA_TOKEN=your_figma_token_here
FIGMA_FILEKEY=your_figma_file_key_here
"""
    
    if not os.path.exists('.env'):
        with open('.env.example', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env.example ファイルを作成しました")
        print("📝 .env.example を .env にコピーして、実際のAPI情報を設定してください")
    else:
        print("📄 .env ファイルは既に存在します")

def check_requirements():
    """requirements.txtの内容を確認"""
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt が存在します")
        print("📦 依存関係をインストールするには: pip install -r requirements.txt")
    else:
        print("❌ requirements.txt が見つかりません")

def main():
    print("🚀 Template Image Creator セットアップを開始します...")
    print("-" * 50)
    
    # ディレクトリ作成
    create_directories()
    print()
    
    # 環境変数ファイル作成
    create_env_file()
    print()
    
    # requirements.txt確認
    check_requirements()
    print()
    
    print("-" * 50)
    print("✨ セットアップが完了しました！")
    print()
    print("次のステップ:")
    print("1. pip install -r requirements.txt")
    print("2. templates/ フォルダにテンプレート画像を配置")
    print("3. fonts/ フォルダにフォントファイルを配置")
    print("4. .env ファイルにFigma API情報を設定")
    print("5. streamlit run app.py でアプリを起動")

if __name__ == "__main__":
    main() 