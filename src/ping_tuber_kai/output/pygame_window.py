"""PyGame表示モジュール."""

from pathlib import Path

import pygame

from ..config import settings
from ..lipsync.viseme import Viseme, get_viseme_image_name


class PygameWindow:
    """PyGameウィンドウ."""

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        title: str = "ping-tuber-kai",
        assets_dir: Path | None = None,
    ):
        """初期化.

        Args:
            width: ウィンドウ幅
            height: ウィンドウ高さ
            title: ウィンドウタイトル
            assets_dir: 口形状アセットディレクトリ
        """
        self.width = width or settings.window_width
        self.height = height or settings.window_height
        self.title = title
        self.assets_dir = assets_dir or settings.mouth_assets_dir

        self._screen: pygame.Surface | None = None
        self._clock: pygame.time.Clock | None = None
        self._images: dict[Viseme, pygame.Surface] = {}
        self._current_viseme: Viseme = Viseme.CLOSED
        self._running: bool = False
        self._initialized: bool = False

    def init(self) -> None:
        """PyGame初期化."""
        if self._initialized:
            return

        pygame.init()
        self._screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self._clock = pygame.time.Clock()
        self._load_images()
        self._initialized = True

    def _load_images(self) -> None:
        """口形状画像を読み込み."""
        for viseme in Viseme:
            image_path = self.assets_dir / get_viseme_image_name(viseme)
            if image_path.exists():
                img = pygame.image.load(str(image_path))
                # ウィンドウサイズにスケール
                img = pygame.transform.scale(img, (self.width, self.height))
                self._images[viseme] = img
            else:
                # 画像がない場合はプレースホルダーを生成
                self._images[viseme] = self._create_placeholder(viseme)

    def _create_placeholder(self, viseme: Viseme) -> pygame.Surface:
        """プレースホルダー画像を生成.

        Args:
            viseme: 口形状

        Returns:
            pygame.Surface: プレースホルダー画像
        """
        surface = pygame.Surface((self.width, self.height))
        surface.fill((50, 50, 50))  # ダークグレー背景

        # Viseme名を表示
        font = pygame.font.Font(None, 72)
        text = font.render(viseme.value.upper(), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(text, text_rect)

        # 口の形を簡易描画
        mouth_shapes = {
            Viseme.A: (100, 60),  # 大きく開く
            Viseme.I: (80, 20),  # 横に広げる
            Viseme.U: (30, 40),  # すぼめる
            Viseme.E: (70, 30),  # 少し開く+横
            Viseme.O: (50, 50),  # 丸く開く
            Viseme.N: (40, 10),  # 軽く閉じ
            Viseme.CLOSED: (40, 5),  # 閉じ
        }
        w, h = mouth_shapes.get(viseme, (40, 20))
        mouth_rect = pygame.Rect(
            (self.width - w) // 2,
            self.height // 2 + 50,
            w,
            h,
        )
        pygame.draw.ellipse(surface, (200, 100, 100), mouth_rect)

        return surface

    def set_viseme(self, viseme: Viseme) -> None:
        """表示するVisemeを設定.

        Args:
            viseme: 口形状
        """
        self._current_viseme = viseme

    def update(self) -> bool:
        """画面更新.

        Returns:
            bool: 継続する場合True、終了する場合False
        """
        if not self._initialized or self._screen is None:
            return False

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        # 描画
        if self._current_viseme in self._images:
            self._screen.blit(self._images[self._current_viseme], (0, 0))
        else:
            self._screen.fill((0, 0, 0))

        pygame.display.flip()
        return True

    def tick(self, fps: int | None = None) -> float:
        """フレームレート制御.

        Args:
            fps: フレームレート（デフォルト: 設定から取得）

        Returns:
            float: 前フレームからの経過時間（ミリ秒）
        """
        if self._clock is None:
            return 0.0
        return self._clock.tick(fps or settings.fps)

    def quit(self) -> None:
        """PyGame終了."""
        if self._initialized:
            pygame.quit()
            self._initialized = False
            self._screen = None
            self._clock = None
            self._images.clear()

    def __enter__(self) -> "PygameWindow":
        self.init()
        return self

    def __exit__(self, *args) -> None:
        self.quit()

    @property
    def is_initialized(self) -> bool:
        """初期化済みかどうか."""
        return self._initialized
