"""統合GUIアプリ."""

from pathlib import Path

import pygame

from ..config import settings
from ..lipsync.viseme import Viseme
from ..output.obs_websocket import OBSController, is_obs_available
from ..output.pygame_window import PygameWindow
from ..player.sync import SyncEngine
from ..voicevox.client import VoicevoxClient


class App:
    """統合GUIアプリケーション."""

    def __init__(
        self,
        use_obs: bool = False,
        assets_dir: Path | None = None,
    ):
        """初期化.

        Args:
            use_obs: OBS WebSocket連携を使用するか
            assets_dir: アセットディレクトリ
        """
        self.use_obs = use_obs and is_obs_available()
        self.assets_dir = assets_dir

        self._voicevox: VoicevoxClient | None = None
        self._sync_engine: SyncEngine | None = None
        self._window: PygameWindow | None = None
        self._obs: OBSController | None = None
        self._running: bool = False

    def init(self) -> None:
        """アプリケーション初期化."""
        # VOICEVOXクライアント
        self._voicevox = VoicevoxClient()

        # 同期エンジン
        self._sync_engine = SyncEngine(fps=settings.fps)

        # PyGameウィンドウ
        self._window = PygameWindow(assets_dir=self.assets_dir)
        self._window.init()

        # OBS連携（オプション）
        if self.use_obs:
            try:
                self._obs = OBSController()
                self._obs.connect()
            except Exception as e:
                print(f"OBS connection failed: {e}")
                self._obs = None

    def speak(self, text: str, speaker_id: int | None = None) -> None:
        """テキストを発話.

        Args:
            text: 発話テキスト
            speaker_id: 話者ID
        """
        if self._voicevox is None or self._sync_engine is None:
            raise RuntimeError("App not initialized. Call init() first.")

        # VOICEVOX APIから音声生成
        query, audio = self._voicevox.speak(text, speaker_id)

        # 同期エンジンに準備
        self._sync_engine.prepare(query, audio)

        # 再生開始
        self._sync_engine.play()

    def run(self, text: str | None = None, speaker_id: int | None = None) -> None:
        """メインループ実行.

        Args:
            text: 発話テキスト（指定時は自動再生）
            speaker_id: 話者ID
        """
        if self._window is None or self._sync_engine is None:
            raise RuntimeError("App not initialized. Call init() first.")

        self._running = True

        # テキスト指定時は自動再生
        if text:
            self.speak(text, speaker_id)

        while self._running:
            # フレーム更新
            viseme = self._sync_engine.update()

            # 表示更新
            self._update_viseme(viseme)

            # PyGame更新
            if not self._window.update():
                self._running = False
                break

            # フレームレート制御
            self._window.tick()

            # 再生完了チェック
            if text and not self._sync_engine.is_playing:
                # 再生完了後も少し待機
                pygame.time.wait(500)
                self._running = False

    def _update_viseme(self, viseme: Viseme) -> None:
        """Viseme更新.

        Args:
            viseme: 口形状
        """
        # PyGame表示
        if self._window is not None:
            self._window.set_viseme(viseme)

        # OBS更新
        if self._obs is not None:
            self._obs.set_viseme(viseme)

    def quit(self) -> None:
        """アプリケーション終了."""
        self._running = False

        if self._sync_engine is not None:
            self._sync_engine.stop()

        if self._obs is not None:
            self._obs.hide_all()
            self._obs.disconnect()

        if self._window is not None:
            self._window.quit()

        if self._voicevox is not None:
            self._voicevox.close()

    def __enter__(self) -> "App":
        self.init()
        return self

    def __exit__(self, *args) -> None:
        self.quit()

    @property
    def is_running(self) -> bool:
        """実行中かどうか."""
        return self._running
