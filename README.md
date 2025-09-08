# Template Image Creator

テンプレート素材に文字とイラストを入れた画像生成アプリです。

## 🚀 主な機能
- **Figmaテンプレート連携**: Figma APIから動的にテンプレートを取得・選択
- **ローカルテンプレート対応**: 従来通りのローカルファイル使用も可能
- **カスタムテキスト合成**: 日本語テキストの自然な改行処理
- **ランダムイラスト挿入**: Figmaから自動でイラストを取得・挿入
- **複数画像一括生成**: テキスト一覧から複数画像を一度に生成
- **ZIP形式ダウンロード**: 個別またはZIP形式での一括ダウンロード
- **ZenOldMincho-Boldフォント**: デフォルトで美しい日本語フォントを使用

## セットアップ
1. 必要なライブラリをインストール
   ```bash
   pip install -r requirements.txt
   ```

2. `.env`ファイルを作成し、Figma API情報を設定（Figmaテンプレートを使用する場合）
   ```bash
   cp .env.example .env
   # .envファイルを編集して実際のAPI情報を設定
   ```
   
   **Figma API情報の取得方法**:
   - `FIGMA_TOKEN`: [Figma個人設定](https://www.figma.com/settings)でPersonal Access Tokenを作成
   - `FIGMA_FILEKEY`: FigmaファイルのURLから取得 (`figma.com/file/FILE_KEY/...`)

3. テンプレート画像を`templates/`フォルダに配置

4. フォントファイルを`fonts/`フォルダに配置

## 使い方
```bash
streamlit run app.py
```

## フォルダ構成
- `app.py`: メインアプリケーション
- `core.py`: 画像処理のコア機能
- `templates/`: テンプレート画像
- `fonts/`: フォントファイル
- `img/`: 生成された画像の保存先 