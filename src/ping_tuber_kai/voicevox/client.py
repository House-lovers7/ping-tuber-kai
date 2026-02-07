"""VOICEVOX API クライアント."""

import httpx

from ..config import settings
from .models import AudioQuery, Speaker


class VoicevoxError(Exception):
    """VOICEVOX APIエラー."""

    pass


class VoicevoxClient:
    """VOICEVOX Engine APIクライアント."""

    def __init__(self, host: str | None = None, timeout: float = 30.0):
        """初期化.

        Args:
            host: VOICEVOX Engine URL（デフォルト: 設定から取得）
            timeout: タイムアウト秒数
        """
        self.host = host or settings.voicevox_host
        self.timeout = timeout
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """HTTPクライアント（遅延初期化）."""
        if self._client is None:
            self._client = httpx.Client(base_url=self.host, timeout=self.timeout)
        return self._client

    def close(self) -> None:
        """クライアントを閉じる."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "VoicevoxClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def audio_query(self, text: str, speaker_id: int | None = None) -> AudioQuery:
        """音声合成クエリを生成.

        Args:
            text: 合成するテキスト
            speaker_id: 話者ID（デフォルト: 設定から取得）

        Returns:
            AudioQuery: 音声合成クエリ

        Raises:
            VoicevoxError: API呼び出しに失敗した場合
        """
        speaker = speaker_id if speaker_id is not None else settings.voicevox_speaker_id

        try:
            response = self.client.post(
                "/audio_query",
                params={"text": text, "speaker": speaker},
            )
            response.raise_for_status()
            return AudioQuery.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            raise VoicevoxError(f"audio_query failed: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise VoicevoxError(f"Request failed: {e}") from e

    def synthesis(self, query: AudioQuery, speaker_id: int | None = None) -> bytes:
        """音声を合成.

        Args:
            query: 音声合成クエリ
            speaker_id: 話者ID（デフォルト: 設定から取得）

        Returns:
            bytes: WAV形式の音声データ

        Raises:
            VoicevoxError: API呼び出しに失敗した場合
        """
        speaker = speaker_id if speaker_id is not None else settings.voicevox_speaker_id

        try:
            response = self.client.post(
                "/synthesis",
                params={"speaker": speaker},
                json=query.model_dump(by_alias=True),
            )
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            raise VoicevoxError(f"synthesis failed: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise VoicevoxError(f"Request failed: {e}") from e

    def speak(self, text: str, speaker_id: int | None = None) -> tuple[AudioQuery, bytes]:
        """テキストから音声を合成（audio_query + synthesis）.

        Args:
            text: 合成するテキスト
            speaker_id: 話者ID（デフォルト: 設定から取得）

        Returns:
            tuple[AudioQuery, bytes]: (音声クエリ, WAV音声データ)
        """
        query = self.audio_query(text, speaker_id)
        audio = self.synthesis(query, speaker_id)
        return query, audio

    def get_speakers(self) -> list[Speaker]:
        """話者一覧を取得.

        Returns:
            list[Speaker]: 話者リスト

        Raises:
            VoicevoxError: API呼び出しに失敗した場合
        """
        try:
            response = self.client.get("/speakers")
            response.raise_for_status()
            return [Speaker.model_validate(s) for s in response.json()]
        except httpx.HTTPStatusError as e:
            raise VoicevoxError(f"get_speakers failed: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise VoicevoxError(f"Request failed: {e}") from e

    def is_available(self) -> bool:
        """VOICEVOX Engineが利用可能か確認.

        Returns:
            bool: 利用可能な場合True
        """
        try:
            response = self.client.get("/version")
            return response.status_code == 200
        except httpx.RequestError:
            return False
