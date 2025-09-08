import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv
import re  # テキスト改行機能用
import textwrap  # テキスト改行機能用

# .envファイルを読み込み
load_dotenv()

# 環境変数から設定を取得
FIGMA_TOKEN = os.getenv('FIGMA_TOKEN')
FIGMA_FILEKEY = os.getenv('FIGMA_FILEKEY')

def get_template_frames():
    """Figmaから背景テンプレートフレームを取得"""
    if not FIGMA_TOKEN or not FIGMA_FILEKEY:
        return []
        
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/files/{FIGMA_FILEKEY}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
            
        data = response.json()
        
        # 🛬 Assets ページの background セクションを探す
        templates = []
        for page in data["document"]["children"]:
            if page.get("name") == "🛬 Assets":
                for child in page["children"]:
                    if child.get("name") == "background":
                        for frame in child["children"]:
                            if frame["type"] == "FRAME":
                                templates.append({
                                    "id": frame["id"],
                                    "name": frame["name"]
                                })
        
        print(f"✅ テンプレート {len(templates)}個を取得しました")
        return templates
        
    except Exception as e:
        print(f"テンプレート取得エラー: {e}")
        return []

def get_template_image(frame_id):
    """指定フレームの画像を取得して表示用PIL Imageとして返す"""
    if not FIGMA_TOKEN or not FIGMA_FILEKEY:
        return None
        
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/images/{FIGMA_FILEKEY}?ids={frame_id}&format=png&scale=1"
    
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
        print(f"画像取得エラー: {e}")
        return None

def get_random_illustration():
    """ランダムなイラストを取得"""
    if not FIGMA_TOKEN or not FIGMA_FILEKEY:
        return None
        
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/files/{FIGMA_FILEKEY}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        # 🛬 Assets ページの illustration セクションを探す
        illustrations = []
        for page in data["document"]["children"]:
            if page.get("name") == "🛬 Assets":
                for child in page["children"]:
                    if child.get("name") == "illustration":
                        illustrations.extend(child.get("children", []))
                        break
                break
        
        if not illustrations:
            return None
            
        # ランダムなイラストを選択
        import random
        selected = random.choice(illustrations)
        
        # イラスト画像をダウンロード
        img_url = f"https://api.figma.com/v1/images/{FIGMA_FILEKEY}?ids={selected['id']}&format=png&scale=1"
        res = requests.get(img_url, headers=headers)
        if res.status_code != 200:
            return None
            
        img_data = res.json()
        image_url = img_data.get("images", {}).get(selected['id'])
        if not image_url:
            return None
            
        # 画像データをダウンロード
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            return Image.open(BytesIO(img_response.content))
            
    except Exception as e:
        print(f"イラスト取得エラー: {e}")
        
    return None

def get_illustration_frames():
    """Figmaからイラスト素材フレームを取得"""
    if not FIGMA_TOKEN or not FIGMA_FILEKEY:
        return []
        
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/files/{FIGMA_FILEKEY}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
            
        data = response.json()
        
        # 🛬 Assets ページの illustration セクションを探す
        illustrations = []
        for page in data["document"]["children"]:
            if page.get("name") == "🛬 Assets":
                for child in page["children"]:
                    if child.get("name") == "illustration":
                        illustrations.extend(child.get("children", []))
                        break
                break
        
        return illustrations
        
    except Exception as e:
        print(f"イラスト素材フレーム取得エラー: {e}")
        return []

def get_illustration_image(frame_id):
    """指定フレームのイラスト画像を取得してPIL Imageとして返す"""
    if not FIGMA_TOKEN or not FIGMA_FILEKEY:
        return None
        
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/images/{FIGMA_FILEKEY}?ids={frame_id}&format=png&scale=1"
    
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
        print(f"イラスト画像取得エラー: {e}")
        return None

def wrap_text(draw, text, font, max_width):
    """テキストを指定幅で自然に改行（句読点が行頭に来ないように）"""
    if not text:
        return []
    
    # まず全体のテキスト幅をチェック
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    
    if text_width <= max_width:
        return [text]  # 改行不要
    
    # 禁則文字（行頭に来てはいけない文字）
    forbidden_start_chars = ['、', '。', '！', '？', '）', '］', '｝', '」', '』', '〉', '》', '〕', '〗', '〙', '〛', 
                            ',', '.', '!', '?', ')', ']', '}', '"', "'", ':', ';']
    
    # 改行しにくい文字（直前での改行を避けたい文字）
    avoid_break_before = ['？', '?', '！', '!', '。', '、', ',', '.']
    
    # 改行しやすい区切り文字
    break_chars = ['の', 'を', 'に', 'で', 'と', 'が', 'は', 'も', 'へ', 'から', 'まで', ' ', '　']
    
    # 文字単位で改行処理（禁則処理対応＋自然な区切り優先）
    lines = []
    current_line = ""
    
    i = 0
    while i < len(text):
        char = text[i]
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]
        
        if test_width <= max_width:
            current_line = test_line
            i += 1
        else:
            # 改行が必要な場合
            if current_line:
                # 禁則処理：次の文字が禁則文字なら、現在行に含める
                if i < len(text) and text[i] in forbidden_start_chars:
                    # 禁則文字を現在行に追加（幅を超えても）
                    current_line += char
                    i += 1
                    best_break = len(current_line)
                else:
                    # 自然な区切り位置を探す（避けるべき文字の直前は除外）
                    best_break = len(current_line)
                    for j in range(len(current_line) - 1, max(0, len(current_line) - 8), -1):
                        # 区切り文字かつ、次の文字が避けるべき文字でない場合
                        if (current_line[j] in break_chars and 
                            (j + 1 >= len(current_line) or current_line[j + 1] not in avoid_break_before)):
                            best_break = j + 1
                            break
                
                # 最適な位置で改行
                if best_break < len(current_line):
                    lines.append(current_line[:best_break])
                    current_line = current_line[best_break:]
                else:
                    lines.append(current_line)
                    current_line = ""
            else:
                # 1文字でも収まらない場合は強制的に追加
                lines.append(char)
                i += 1
    
    if current_line:
        lines.append(current_line)
    
    return lines

def create_image_with_text(template_image, title, subtitle="", layout_horizontal=False, illustration_image=None, title_manual_lines=None, image_type="アイキャッチ画像"):
    """テンプレート画像にテキストとイラストを追加して新しい画像を生成"""
    if template_image is None:
        return None
        
    try:
        # テンプレート画像をコピー
        image = template_image.copy().convert("RGBA")
        draw = ImageDraw.Draw(image)
        
        # フォント設定（高解像度対応 - scale=2で120px/80px）
        font_path = "/Users/ryosuke884/Desktop/Obsidian/03_Output/App/Template-Image-Creator/fonts/ZenOldMincho-Bold.ttf"
        try:
            # 高解像度用にフォントサイズを2倍に調整
            title_font = ImageFont.truetype(font_path, 120)  # 60px → 120px
            subtitle_font = ImageFont.truetype(font_path, 80)  # 40px → 80px
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # 画像サイズを取得
        img_width, img_height = image.size
        
        # イラストを決定（指定があればそれを使用、なければランダム）
        if illustration_image is not None:
            illustration = illustration_image
            print("✅ 指定されたイラストを使用")
        else:
            illustration = get_random_illustration()
            print("✅ ランダムイラストを使用")
        
        # 画像タイプによってレイアウトを決定
        if image_type == "挿入画像":
            # 挿入画像レイアウト（テキスト中央揃え）
            print(f"✅ 挿入画像モード: テキスト中央揃え")
            
            # テキスト改行処理（手動指定優先）
            max_text_width = int(img_width * 0.8)  # 画面の80%幅
            
            if title_manual_lines:
                title_lines = title_manual_lines
                print(f"✅ 挿入画像 手動改行使用: {len(title_lines)}行")
            else:
                title_lines = wrap_text(draw, title, title_font, max_text_width) if title else []
                print(f"✅ 挿入画像 自動改行: {len(title_lines)}行")
            
            # 画面の8割を使用する高さ配分計算（余白改善版）
            total_available_height = int(img_height * 0.75)  # 画面の75%（余白拡大のため）
            margin_top = int(img_height * 0.15)  # 上余白（画面の15%に拡大）
            margin_bottom = int(img_height * 0.1)  # 下余白（画面の10%）
            
            line_spacing = 160
            text_gap = 120  # テキストとイラストの間隔（80px→120px）
            
            # テキストの実際の高さを計算
            text_total_height = len(title_lines) * line_spacing if title_lines else 0
            
            # イラストに使用できる高さを計算
            available_for_illustration = total_available_height - text_total_height - text_gap
            
            # テキストを水平方向のみ中央揃えで描画
            current_y = margin_top
            for line in title_lines:
                # 各行を水平方向のみ中央揃え
                bbox = draw.textbbox((0, 0), line, font=title_font)
                line_width = bbox[2] - bbox[0]
                line_x = (img_width - line_width) // 2
                
                draw.text((line_x, current_y), line, font=title_font, fill=(0, 0, 0, 255))
                current_y += line_spacing
            
            # イラストを残りの高さを最大限活用して配置
            if illustration and available_for_illustration > 200:  # 最小高さ200px確保
                # イラストの縦横比を保持しながら、利用可能な高さに合わせる
                aspect_ratio = illustration.width / illustration.height
                
                # 高さを基準にサイズを決定
                target_height = min(available_for_illustration, int(img_height * 0.6))  # 最大でも画面の60%
                target_width = int(target_height * aspect_ratio)
                
                # 幅が画面幅を超える場合は幅を基準にリサイズ
                margin_sides = 200  # 左右余白
                if target_width > img_width - margin_sides:
                    target_width = img_width - margin_sides
                    target_height = int(target_width / aspect_ratio)
                
                illustration_resized = illustration.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # イラストをテキストの下、中央に配置
                illust_x = (img_width - target_width) // 2
                illust_y = current_y + text_gap
                
                # 下余白を確保するため、位置を調整
                if illust_y + target_height > img_height - margin_bottom:
                    illust_y = img_height - margin_bottom - target_height
                
                if illustration_resized.mode != 'RGBA':
                    illustration_resized = illustration_resized.convert('RGBA')
                image.paste(illustration_resized, (illust_x, illust_y), illustration_resized)
                
                # 実際の使用率を計算
                actual_used_height = (illust_y + target_height) - margin_top
                usage_ratio = actual_used_height / img_height
                
                print(f"✅ 挿入画像 効率配置: テキスト高さ={text_total_height}px, イラスト={target_width}x{target_height}px, 使用率={usage_ratio:.1%}")
            else:
                print(f"⚠️ 挿入画像 イラスト省略: 利用可能高さ不足 ({available_for_illustration}px)")
            
            subtitle_lines = []  # 挿入画像ではサブタイトルなし
            
        elif layout_horizontal:
            # 横並びレイアウト（アイキャッチ画像）- 改善版
            # 画面の8割を使用する高さ配分計算
            total_available_height = int(img_height * 0.8)  # 画面の8割
            margin_top = int(img_height * 0.1)  # 上余白（画面の10%）
            margin_bottom = int(img_height * 0.1)  # 下余白（画面の10%）
            margin_x = 300  # 左右余白
            
            content_w = img_width - margin_x * 2
            content_h = total_available_height
            
            # イラスト領域（左30%）
            illust_area_w = int(content_w * 0.30)
            illust_area_h = content_h
            illust_area_x = margin_x
            illust_area_y = margin_top
            
            # テキスト領域（右70%）
            text_area_x = margin_x + illust_area_w
            text_area_y = margin_top
            text_area_w = int(content_w * 0.70)
            text_area_h = content_h
            text_pad_x = 120  # テキスト領域の左余白
            text_pad_y = 80   # テキスト領域の上余白
            
            line_spacing = 160
            
            # タイトル改行処理（手動指定優先）
            if title_manual_lines:
                title_lines = title_manual_lines
                print(f"✅ 横並び 手動改行使用: {len(title_lines)}行")
            else:
                text_max_width = min(text_area_w - text_pad_x * 2, int(img_width * 0.4))  # テキスト幅調整
                title_lines = wrap_text(draw, title, title_font, text_max_width) if title else []
                print(f"✅ 横並び 自動改行: {len(title_lines)}行")
            
            # テキストの実際の高さを計算
            text_total_height = len(title_lines) * line_spacing if title_lines else 0
            if subtitle:
                subtitle_lines = wrap_text(draw, subtitle, subtitle_font, text_max_width)
                text_total_height += len(subtitle_lines) * 120 + 80  # サブタイトル + 間隔
            else:
                subtitle_lines = []
            
            # テキストを垂直中央に配置（サブタイトルがない場合）
            if not subtitle and title_lines:
                # テキスト領域の垂直中央に配置
                current_text_y = text_area_y + (text_area_h - text_total_height) // 2
                print(f"✅ 横並び 垂直中央配置: タイトル行数={len(title_lines)}, 開始Y={current_text_y}")
            else:
                current_text_y = text_area_y + text_pad_y
            
            # タイトルを描画
            if title_lines:
                for line in title_lines:
                    draw.text((text_area_x + text_pad_x, current_text_y), 
                             line, font=title_font, fill=(0, 0, 0, 255))
                    current_text_y += line_spacing
                current_text_y += 80  # タイトル・サブタイトル間の余白
            
            # サブタイトルを描画
            if subtitle_lines:
                for line in subtitle_lines:
                    draw.text((text_area_x + text_pad_x, current_text_y), 
                             line, font=subtitle_font, fill=(100, 100, 100, 255))
                    current_text_y += 120
            
            # イラストをテキスト量に応じて動的にサイズ調整
            if illustration:
                # テキスト量に応じてイラストサイズを決定
                text_usage_ratio = text_total_height / content_h
                
                if text_usage_ratio < 0.3:  # テキストが少ない場合
                    illust_scale = 0.95  # イラストを大きく
                elif text_usage_ratio < 0.6:  # テキストが中程度
                    illust_scale = 0.85  # 標準サイズ
                else:  # テキストが多い場合
                    illust_scale = 0.75  # イラストを小さく
                
                scale = min(illust_area_w / illustration.width, illust_area_h / illustration.height) * illust_scale
                new_w = int(illustration.width * scale)
                new_h = int(illustration.height * scale)
                illustration_resized = illustration.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # イラストを左側領域の中央に配置
                paste_x = illust_area_x + (illust_area_w - new_w) // 2
                paste_y = illust_area_y + (illust_area_h - new_h) // 2
                
                if illustration_resized.mode != 'RGBA':
                    illustration_resized = illustration_resized.convert('RGBA')
                image.paste(illustration_resized, (paste_x, paste_y), illustration_resized)
                
                print(f"✅ 横並び 動的サイズ: イラスト={new_w}x{new_h}, テキスト使用率={text_usage_ratio:.1%}, スケール={illust_scale:.2f}")
            else:
                subtitle_lines = []
        
        else:
            # 縦並びレイアウト（アイキャッチ画像）- 改善版
            # 画面の8割を使用する高さ配分計算
            total_available_height = int(img_height * 0.8)  # 画面の8割
            margin_top = int(img_height * 0.1)  # 上余白（画面の10%）
            margin_bottom = int(img_height * 0.1)  # 下余白（画面の10%）
            margin_left = 200  # 左余白
            
            line_spacing = 160
            text_illustration_gap = 120  # テキストとイラストの間隔
            
            # テキスト描画可能な最大幅を計算（全体の70%、ロゴ回避）
            max_text_width = int(img_width * 0.7)
            
            # タイトル改行処理（手動指定優先）
            if title_manual_lines:
                title_lines = title_manual_lines
                print(f"✅ 縦並び 手動改行使用: {len(title_lines)}行")
            else:
                title_lines = wrap_text(draw, title, title_font, max_text_width) if title else []
                print(f"✅ 縦並び 自動改行: {len(title_lines)}行")
            
            # テキストの実際の高さを計算
            text_total_height = len(title_lines) * line_spacing if title_lines else 0
            if subtitle:
                subtitle_lines = wrap_text(draw, subtitle, subtitle_font, max_text_width)
                text_total_height += len(subtitle_lines) * 120 + 240  # サブタイトル + 間隔
            else:
                subtitle_lines = []
            
            # イラストに使用できる高さを計算
            available_for_illustration = total_available_height - text_total_height - text_illustration_gap
            
            # タイトルを描画
            current_y = margin_top
            if title_lines:
                for line in title_lines:
                    draw.text((margin_left, current_y), line, font=title_font, fill=(0, 0, 0, 255))
                    current_y += line_spacing
                current_y += 240  # タイトル・サブタイトル間の余白
            
            # サブタイトルを描画
            if subtitle_lines:
                for line in subtitle_lines:
                    draw.text((margin_left, current_y), line, font=subtitle_font, fill=(100, 100, 100, 255))
                    current_y += 120
            
            # イラストを残りの高さを最大限活用して配置
            if illustration and available_for_illustration > 200:  # 最小高さ200px確保
                # イラストの縦横比を保持しながら、利用可能な高さに合わせる
                aspect_ratio = illustration.width / illustration.height
                
                # 高さを基準にサイズを決定
                target_height = min(available_for_illustration, int(img_height * 0.5))  # 最大でも画面の50%
                target_width = int(target_height * aspect_ratio)
                
                # 幅が画面幅を超える場合は幅を基準にリサイズ
                margin_sides = 300
                if target_width > img_width - margin_sides:
                    target_width = img_width - margin_sides
                    target_height = int(target_width / aspect_ratio)
                
                illustration_resized = illustration.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # イラストをテキストの下、中央に配置
                illustration_x = (img_width - target_width) // 2
                illustration_y = current_y + text_illustration_gap
                
                # 下余白を確保するため、位置を調整
                if illustration_y + target_height > img_height - margin_bottom:
                    illustration_y = img_height - margin_bottom - target_height
                
                if illustration_resized.mode != 'RGBA':
                    illustration_resized = illustration_resized.convert('RGBA')
                image.paste(illustration_resized, (illustration_x, illustration_y), illustration_resized)
                
                # 実際の使用率を計算
                actual_used_height = (illustration_y + target_height) - margin_top
                usage_ratio = actual_used_height / img_height
                
                print(f"✅ 縦並び 効率配置: テキスト高さ={text_total_height}px, イラスト={target_width}x{target_height}px, 使用率={usage_ratio:.1%}")
            else:
                print(f"⚠️ 縦並び イラスト省略: 利用可能高さ不足 ({available_for_illustration}px)")
            
        # 使用された改行結果を返すために辞書形式で返す
        result = {
            'image': image,
            'title_lines': title_lines if 'title_lines' in locals() else [],
            'subtitle_lines': subtitle_lines if subtitle and 'subtitle_lines' in locals() else []
        }
        return result
        
    except Exception as e:
        print(f"画像生成エラー: {e}")
        return None
 