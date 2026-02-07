"""VOICEVOX API Pydanticモデル定義."""

from pydantic import BaseModel, Field


class Mora(BaseModel):
    """モーラ（音素単位）."""

    text: str = Field(description="表示用テキスト（カタカナ）")
    consonant: str | None = Field(default=None, description="子音")
    consonant_length: float | None = Field(default=None, description="子音の長さ（秒）")
    vowel: str = Field(description="母音")
    vowel_length: float = Field(description="母音の長さ（秒）")
    pitch: float = Field(description="ピッチ（音高）")

    @property
    def total_length(self) -> float:
        """モーラの総長さ（秒）."""
        consonant_len = self.consonant_length or 0.0
        return consonant_len + self.vowel_length

    @property
    def is_voiced_vowel(self) -> bool:
        """有声母音かどうか（小文字=有声、大文字=無声）."""
        return self.vowel.islower() or self.vowel == "N"


class AccentPhrase(BaseModel):
    """アクセント句."""

    moras: list[Mora] = Field(description="モーラのリスト")
    accent: int = Field(description="アクセント位置")
    pause_mora: Mora | None = Field(default=None, description="ポーズモーラ")
    is_interrogative: bool = Field(default=False, description="疑問文かどうか")


class AudioQuery(BaseModel):
    """音声合成クエリ."""

    accent_phrases: list[AccentPhrase] = Field(description="アクセント句のリスト")
    speed_scale: float = Field(default=1.0, alias="speedScale", description="話速")
    pitch_scale: float = Field(default=0.0, alias="pitchScale", description="音高")
    intonation_scale: float = Field(default=1.0, alias="intonationScale", description="抑揚")
    volume_scale: float = Field(default=1.0, alias="volumeScale", description="音量")
    pre_phoneme_length: float = Field(
        default=0.1, alias="prePhonemeLength", description="開始無音"
    )
    post_phoneme_length: float = Field(
        default=0.1, alias="postPhonemeLength", description="終了無音"
    )
    output_sampling_rate: int = Field(
        default=24000, alias="outputSamplingRate", description="サンプリングレート"
    )
    output_stereo: bool = Field(default=False, alias="outputStereo", description="ステレオ出力")
    kana: str | None = Field(default=None, description="読み仮名")

    model_config = {"populate_by_name": True}


class Speaker(BaseModel):
    """話者情報."""

    name: str = Field(description="話者名")
    speaker_uuid: str = Field(description="話者UUID")
    styles: list["SpeakerStyle"] = Field(description="スタイル一覧")


class SpeakerStyle(BaseModel):
    """話者スタイル."""

    name: str = Field(description="スタイル名")
    id: int = Field(description="スタイルID（speaker_id）")
