#!/usr/bin/env python3
"""PyGame表示テストスクリプト（VOICEVOX不要）."""

import time
from pathlib import Path

import pygame

from ping_tuber_kai.lipsync.viseme import Viseme
from ping_tuber_kai.output.pygame_window import PygameWindow


def main():
    """メイン関数."""
    assets_dir = Path(__file__).parent.parent / "assets" / "mouth"

    print("PyGame Display Test")
    print("=" * 40)
    print(f"Assets directory: {assets_dir}")
    print("Press ESC to exit, or wait for auto-cycle")
    print()

    with PygameWindow(assets_dir=assets_dir) as window:
        # 各Visemeを順番に表示
        visemes = list(Viseme)
        current_index = 0
        last_switch = time.time()
        switch_interval = 0.5  # 0.5秒ごとに切り替え

        running = True
        while running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # 0.5秒ごとにVisemeを切り替え
            now = time.time()
            if now - last_switch >= switch_interval:
                current_index = (current_index + 1) % len(visemes)
                last_switch = now
                viseme = visemes[current_index]
                window.set_viseme(viseme)
                print(f"  Displaying: {viseme.value}")

            # 描画更新
            if not window.update():
                running = False

            window.tick(60)

    print("\nTest completed!")


if __name__ == "__main__":
    main()
