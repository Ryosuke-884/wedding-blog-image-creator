import streamlit as st
from core import get_template_frames, get_template_image, create_image_with_text, get_illustration_frames, get_illustration_image
import random
from io import BytesIO
import zipfile
import base64
import os
import requests
from PIL import Image
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def parse_multiple_headlines(text):
    """見出しを解析し、レベルと内容を抽出"""
    headlines = []
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if line.startswith('###'):  # 見出し3は除外
            continue
        elif line.startswith('##'):  # 見出し2（挿入画像）
            headline_text = line[2:].strip()
            if headline_text:
                headlines.append({
                    'text': headline_text,
                    'level': 2,
                    'type': '挿入画像'
                })
        elif line.startswith('#'):  # 見出し1（アイキャッチ画像）
            headline_text = line[1:].strip()
            if headline_text:
                headlines.append({
                    'text': headline_text,
                    'level': 1,
                    'type': 'アイキャッチ画像'
                })

    # 見出しが見つからない場合は全体をアイキャッチとして扱う
    if not headlines and text.strip():
        headlines.append({
            'text': text.strip(),
            'level': 1,
            'type': 'アイキャッチ画像'
        })

    return headlines



def get_high_resolution_template_image(frame_id):
    """高解像度テンプレート画像を取得（scale=2）"""
    FIGMA_TOKEN = os.getenv('FIGMA_TOKEN')
    FIGMA_FILEKEY = os.getenv('FIGMA_FILEKEY')

    if not FIGMA_TOKEN or not FIGMA_FILEKEY:
        return None

    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/images/{FIGMA_FILEKEY}?ids={frame_id}&format=png&scale=2"  # 高解像度

    try:
        # Figma APIから画像URLを取得
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return None

        data = res.json()
        image_url = data.get("images", {}).get(frame_id)
        if not image_url:
            return None

        # 画像データをダウンロード
        img_response = requests.get(image_url)
        if img_response.status_code != 200:
            return None

        # PIL Imageとして返す
        return Image.open(BytesIO(img_response.content))

    except Exception as e:
        print(f"高解像度画像取得エラー: {e}")
        return None

def get_high_resolution_illustration_image(frame_id):
    """高解像度イラスト画像を取得（scale=2）"""
    FIGMA_TOKEN = os.getenv('FIGMA_TOKEN')
    FIGMA_FILEKEY = os.getenv('FIGMA_FILEKEY')

    if not FIGMA_TOKEN or not FIGMA_FILEKEY:
        return None

    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/images/{FIGMA_FILEKEY}?ids={frame_id}&format=png&scale=2"  # 高解像度

    try:
        # Figma APIから画像URLを取得
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return None

        data = res.json()
        image_url = data.get("images", {}).get(frame_id)
        if not image_url:
            return None

        # 画像データをダウンロード
        img_response = requests.get(image_url)
        if img_response.status_code != 200:
            return None

        # PIL Imageとして返す
        return Image.open(BytesIO(img_response.content))

    except Exception as e:
        print(f"高解像度イラスト画像取得エラー: {e}")
        return None

def image_to_bytes(image):
    """PIL ImageをバイトデータとしてPNG形式で出力"""
    img_buffer = BytesIO()
    image.save(img_buffer, format='PNG')
    return img_buffer.getvalue()

def create_download_link(image, filename):
    """画像のダウンロードリンクを作成"""
    img_bytes = image_to_bytes(image)
    b64 = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}" style="text-decoration: none; background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px; display: inline-block;">💾 {filename}をダウンロード</a>'
    return href

def create_zip_download(images_with_names):
    """複数画像をZIPファイルとしてダウンロード"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for image, filename in images_with_names:
            img_bytes = image_to_bytes(image)
            zip_file.writestr(filename, img_bytes)

    zip_bytes = zip_buffer.getvalue()
    b64 = base64.b64encode(zip_bytes).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="generated_images.zip" style="text-decoration: none; background-color: #FF6B6B; color: white; padding: 8px 16px; border-radius: 4px; display: inline-block;">📦 一括ダウンロード (ZIP)</a>'
    return href

def main():
    st.set_page_config(page_title="📝 Template Image Creator", page_icon="🎨", layout="wide")

    st.title("📝 Template Image Creator")
    st.markdown("**見出しテキストを入力して、テンプレート画像を作成しましょう！**")

    # サイドバーでレイアウト設定
    with st.sidebar:
        st.header("⚙️ 設定")

        # レイアウト選択
        layout_horizontal = st.radio(
            "🎨 アイキャッチ画像レイアウト:",
            [False, True],
            format_func=lambda x: "📄 縦並び" if not x else "📝 横並び",
            help="アイキャッチ画像（#）のレイアウト\n※挿入画像（##）は自動で中央揃え"
        )

        st.info("🎨 **高解像度**: 常時ON")
        st.info("🎲 **画像素材**: 全てランダム選択")

    # 初期化（バックグラウンドで実行）
    if 'template_frames' not in st.session_state:
        st.session_state.template_frames = get_template_frames()
    if 'illustration_frames' not in st.session_state:
        st.session_state.illustration_frames = get_illustration_frames()

    # 全てランダム選択に固定
    template_selected, template_random = None, True
    illustration_selected, illustration_random = None, True

    st.markdown("---")

    st.header("✏️ テキスト入力")

    # テキスト入力
    headline_text = st.text_area(
        "📝 見出しテキストを入力してください:",
        value="# 引出物の相場の基本的な考え方\n\n## 親族向けの引出物相場\n\n## 友人向けの引出物相場",
        height=200,
        help="見出しレベル：# = アイキャッチ画像、## = 挿入画像（中央揃え）"
    )

    # 見出し解析
    headlines = parse_multiple_headlines(headline_text)

    if len(headlines) > 1:
        st.success(f"🎯 **{len(headlines)}個の見出し**が検出されました:")
        for i, headline in enumerate(headlines, 1):
            icon = "🖼️" if headline['type'] == "アイキャッチ画像" else "📝"
            st.write(f"　{i}. {icon} **{headline['type']}**: {headline['text']}")
    elif len(headlines) == 1:
        headline = headlines[0]
        icon = "🖼️" if headline['type'] == "アイキャッチ画像" else "📝"
        st.info(f"{icon} **{headline['type']}**: {headline['text']}")
    else:
        st.warning("⚠️ 有効な見出しが見つかりません")

    st.markdown("---")

    # 画像生成ボタン
    if st.button("🎨 画像生成", type="primary", use_container_width=True):
        if not headline_text.strip():
            st.error("❌ 見出しテキストを入力してください。")
        else:
            # 画像生成処理
            if 'generated_results' not in st.session_state:
                st.session_state.generated_results = []

            st.session_state.generated_results = []  # リセット

            # 不要なセッション状態をクリア
            for key in list(st.session_state.keys()):
                if key.startswith(('regeneration_', 'previous_text_')):
                    del st.session_state[key]

            # プログレスバーの準備
            total_images = len(headlines)
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, headline_data in enumerate(headlines, 1):
                headline_text = headline_data['text']
                headline_type = headline_data['type']

                # 進捗表示
                progress = i / total_images
                progress_bar.progress(progress)
                type_icon = "🖼️" if headline_type == "アイキャッチ画像" else "📝"
                status_text.text(f"🎨 画像{i}/{total_images}: {type_icon} {headline_type} '{headline_text}' を生成中...")

                # 各画像ごとに背景テンプレートを決定
                if template_random:
                    selected_template = random.choice(st.session_state.template_frames)
                elif template_selected:
                    selected_template = template_selected
                else:
                    st.error("❌ 背景テンプレートを選択してください。")
                    st.stop()

                # 各画像ごとにイラスト素材を決定
                if illustration_random:
                    selected_illustration = random.choice(st.session_state.illustration_frames)
                elif illustration_selected:
                    selected_illustration = illustration_selected
                else:
                    st.error("❌ イラスト素材を選択してください。")
                    st.stop()

                # テンプレート画像とイラスト画像を取得（常に高解像度）
                template_image = get_high_resolution_template_image(selected_template['id'])
                illustration_image = get_high_resolution_illustration_image(selected_illustration['id'])

                if not template_image:
                    st.error(f"❌ 画像{i}の背景テンプレート画像の取得に失敗しました。")
                    continue

                # 挿入画像の場合はlayout_horizontalは無視
                use_horizontal = layout_horizontal if headline_type == "アイキャッチ画像" else False

                result = create_image_with_text(
                    template_image=template_image,
                    title=headline_text,
                    subtitle="",
                    layout_horizontal=use_horizontal,
                    illustration_image=illustration_image,
                    image_type=headline_type
                )

                if result and result.get('image'):
                    result_image = result['image']
                    title_lines = result.get('title_lines', [])

                    suffix = f"_{i:02d}" if len(headlines) > 1 else ""
                    filename = f"generated_image{suffix}.png"

                    # セッション状態に保存
                    result_data = {
                        'image': result_image,
                        'filename': filename,
                        'title_lines': title_lines,
                        'headline_text': headline_text,
                        'headline_type': headline_type,
                        'template': selected_template,
                        'illustration': selected_illustration,
                        'use_horizontal': use_horizontal,
                        'template_image': template_image,
                        'illustration_image': illustration_image
                    }
                    st.session_state.generated_results.append(result_data)
                else:
                    st.error(f"❌ 画像{i}の生成に失敗しました。")

            # 完了時の表示
            progress_bar.progress(1.0)
            status_text.text(f"✅ 全{total_images}枚の画像生成が完了しました！")

            # 生成された画像を表示（UI整理）
            if hasattr(st.session_state, 'generated_results') and st.session_state.generated_results:
                st.markdown("---")
                st.header("🖼️ 生成結果")

                generated_images = []  # 一括ダウンロード用

                for i, result_data in enumerate(st.session_state.generated_results, 1):
                    with st.container():
                        st.subheader(f"画像 {i}: {result_data['headline_type']}")

                        # 画像表示（セッション状態から最新画像を取得）
                        current_image = st.session_state.generated_results[i-1]['image']
                        current_filename = st.session_state.generated_results[i-1]['filename']

                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.image(current_image, 
                                   caption=f"{result_data['headline_text']}", 
                                   use_container_width=True)
                        with col2:
                            # ダウンロードボタン（最新画像）
                            download_link = create_download_link(current_image, current_filename)
                            st.markdown(download_link, unsafe_allow_html=True)

                        # 改行調整機能を削除（Streamlitの制約により安定動作が困難なため）
                        st.info("💡 改行調整: 生成時に自動で適切な改行が適用されます")


                        generated_images.append((current_image, current_filename))
                        st.markdown("---")

            # 一括ダウンロードボタン（複数画像の場合）
            if len(generated_images) > 1:
                st.markdown("---")
                st.subheader("📦 一括ダウンロード")
                zip_download_link = create_zip_download(generated_images)
                st.markdown(zip_download_link, unsafe_allow_html=True)
                st.info(f"🎯 {len(generated_images)}枚の画像をZIPファイルでまとめてダウンロードできます")

if __name__ == "__main__":
    main()
