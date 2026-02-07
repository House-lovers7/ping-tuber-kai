"""設定管理モジュール."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定."""

    model_config = SettingsConfigDict(
        env_prefix="PING_TUBER_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # VOICEVOX設定
    voicevox_host: str = Field(default="http://localhost:50021", description="VOICEVOX Engine URL")
    voicevox_speaker_id: int = Field(default=1, description="話者ID（デフォルト: ずんだもん）")

    # 音声設定
    audio_sample_rate: int = Field(default=24000, description="サンプリングレート")

    # 表示設定
    window_width: int = Field(default=400, description="ウィンドウ幅")
    window_height: int = Field(default=400, description="ウィンドウ高さ")
    fps: int = Field(default=60, description="フレームレート")

    # アセット設定
    assets_dir: Path = Field(
        default=Path(__file__).parent.parent.parent / "assets",
        description="アセットディレクトリ",
    )

    # OBS設定（オプション）
    obs_host: str = Field(default="localhost", description="OBS WebSocket ホスト")
    obs_port: int = Field(default=4455, description="OBS WebSocket ポート")
    obs_password: str = Field(default="", description="OBS WebSocket パスワード")

    @property
    def mouth_assets_dir(self) -> Path:
        """口形状アセットディレクトリ."""
        return self.assets_dir / "mouth"


# グローバル設定インスタンス
settings = Settings()
