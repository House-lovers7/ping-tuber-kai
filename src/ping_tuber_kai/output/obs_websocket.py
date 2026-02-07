"""OBS WebSocket連携モジュール."""

from ..config import settings
from ..lipsync.viseme import Viseme

# obsws-pythonはオプショナル依存
try:
    import obsws_python as obs

    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False


class OBSWebSocketError(Exception):
    """OBS WebSocketエラー."""

    pass


class OBSController:
    """OBS WebSocketコントローラー."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        password: str | None = None,
        source_prefix: str = "mouth_",
    ):
        """初期化.

        Args:
            host: OBS WebSocketホスト
            port: OBS WebSocketポート
            password: OBS WebSocketパスワード
            source_prefix: 口形状ソースのプレフィックス
        """
        if not OBS_AVAILABLE:
            raise OBSWebSocketError(
                "obsws-python is not installed. Install with: uv sync --extra obs"
            )

        self.host = host or settings.obs_host
        self.port = port or settings.obs_port
        self.password = password or settings.obs_password
        self.source_prefix = source_prefix

        self._client: obs.ReqClient | None = None
        self._current_viseme: Viseme = Viseme.CLOSED
        self._connected: bool = False

    def connect(self) -> None:
        """OBSに接続."""
        if not OBS_AVAILABLE:
            raise OBSWebSocketError("obsws-python is not installed")

        try:
            self._client = obs.ReqClient(
                host=self.host,
                port=self.port,
                password=self.password if self.password else None,
            )
            self._connected = True
        except Exception as e:
            raise OBSWebSocketError(f"Failed to connect to OBS: {e}") from e

    def disconnect(self) -> None:
        """OBSから切断."""
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception:
                pass
            self._client = None
        self._connected = False

    def __enter__(self) -> "OBSController":
        self.connect()
        return self

    def __exit__(self, *args) -> None:
        self.disconnect()

    def set_viseme(self, viseme: Viseme) -> None:
        """表示するVisemeを設定.

        OBS上で対応するソースの表示/非表示を切り替える。
        ソース名は "{source_prefix}{viseme.value}" の形式。
        例: mouth_a, mouth_i, mouth_closed

        Args:
            viseme: 口形状
        """
        if not self._connected or self._client is None:
            return

        if viseme == self._current_viseme:
            return

        # 前のVisemeを非表示
        self._set_source_visible(self._current_viseme, False)

        # 新しいVisemeを表示
        self._set_source_visible(viseme, True)

        self._current_viseme = viseme

    def _set_source_visible(self, viseme: Viseme, visible: bool) -> None:
        """ソースの表示/非表示を設定.

        Args:
            viseme: 口形状
            visible: 表示する場合True
        """
        if self._client is None:
            return

        source_name = f"{self.source_prefix}{viseme.value}"

        try:
            # 現在のシーンを取得
            scene_resp = self._client.get_current_program_scene()
            scene_name = scene_resp.current_program_scene_name

            # シーンアイテムIDを取得
            item_resp = self._client.get_scene_item_id(scene_name, source_name)
            item_id = item_resp.scene_item_id

            # 表示/非表示を設定
            self._client.set_scene_item_enabled(scene_name, item_id, visible)
        except Exception:
            # ソースが存在しない場合などは無視
            pass

    def hide_all(self) -> None:
        """すべての口形状ソースを非表示."""
        for viseme in Viseme:
            self._set_source_visible(viseme, False)

    @property
    def is_connected(self) -> bool:
        """接続中かどうか."""
        return self._connected

    @property
    def current_viseme(self) -> Viseme:
        """現在のViseme."""
        return self._current_viseme


def is_obs_available() -> bool:
    """OBS WebSocket連携が利用可能か.

    Returns:
        bool: obsws-pythonがインストールされている場合True
    """
    return OBS_AVAILABLE
