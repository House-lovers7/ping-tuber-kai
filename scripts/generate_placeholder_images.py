#!/usr/bin/env python3
"""テスト用プレースホルダー口形状画像を生成するスクリプト."""

from pathlib import Path

import pygame

# 口形状の定義（幅, 高さ）
MOUTH_SHAPES = {
    "a": (120, 80),      # あ - 大きく開く
    "i": (100, 25),      # い - 横に広げる
    "u": (40, 50),       # う - すぼめる
    "e": (90, 40),       # え - 少し開く+横
    "o": (60, 60),       # お - 丸く開く
    "n": (50, 15),       # ん - 軽く閉じ
    "closed": (60, 8),   # 閉じ
}

# 画像サイズ
IMAGE_SIZE = (400, 400)

# 色
BG_COLOR = (50, 50, 50)       # ダークグレー背景
FACE_COLOR = (255, 220, 180)  # 肌色
MOUTH_COLOR = (180, 80, 80)   # 口の色
TEXT_COLOR = (255, 255, 255)  # テキスト色


def generate_placeholder_image(viseme: str, size: tuple[int, int]) -> pygame.Surface:
    """プレースホルダー画像を生成.

    Args:
        viseme: 口形状名
        size: 画像サイズ (width, height)

    Returns:
        pygame.Surface: 生成された画像
    """
    width, height = size
    surface = pygame.Surface(size, pygame.SRCALPHA)

    # 背景
    surface.fill(BG_COLOR)

    # 顔の円
    face_center = (width // 2, height // 2)
    face_radius = min(width, height) // 2 - 20
    pygame.draw.circle(surface, FACE_COLOR, face_center, face_radius)

    # 目
    eye_y = height // 2 - 40
    eye_left_x = width // 2 - 50
    eye_right_x = width // 2 + 50
    pygame.draw.circle(surface, (50, 50, 50), (eye_left_x, eye_y), 10)
    pygame.draw.circle(surface, (50, 50, 50), (eye_right_x, eye_y), 10)

    # 口
    mouth_w, mouth_h = MOUTH_SHAPES.get(viseme, (60, 30))
    mouth_x = width // 2 - mouth_w // 2
    mouth_y = height // 2 + 30
    mouth_rect = pygame.Rect(mouth_x, mouth_y, mouth_w, mouth_h)

    if viseme in ("o", "u"):
        # 丸い口
        pygame.draw.ellipse(surface, MOUTH_COLOR, mouth_rect)
    else:
        # 楕円の口
        pygame.draw.ellipse(surface, MOUTH_COLOR, mouth_rect)

    # ラベル
    font = pygame.font.Font(None, 48)
    label = viseme.upper() if viseme != "closed" else "CLOSED"
    text = font.render(label, True, TEXT_COLOR)
    text_rect = text.get_rect(center=(width // 2, height - 30))
    surface.blit(text, text_rect)

    return surface


def main():
    """メイン関数."""
    # PyGame初期化
    pygame.init()

    # 出力ディレクトリ
    output_dir = Path(__file__).parent.parent / "assets" / "mouth"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating placeholder images in: {output_dir}")

    # 各口形状の画像を生成
    for viseme in MOUTH_SHAPES:
        surface = generate_placeholder_image(viseme, IMAGE_SIZE)
        output_path = output_dir / f"{viseme}.png"
        pygame.image.save(surface, str(output_path))
        print(f"  Created: {output_path.name}")

    pygame.quit()
    print("Done!")


if __name__ == "__main__":
    main()
