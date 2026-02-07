"""VOICEVOX モジュールのテスト."""

import pytest

from ping_tuber_kai.voicevox.models import AccentPhrase, AudioQuery, Mora


class TestMora:
    """Moraモデルのテスト."""

    def test_total_length_with_consonant(self):
        """子音ありモーラの総長さ."""
        mora = Mora(
            text="コ",
            consonant="k",
            consonant_length=0.1,
            vowel="o",
            vowel_length=0.15,
            pitch=5.0,
        )
        assert mora.total_length == pytest.approx(0.25)

    def test_total_length_without_consonant(self):
        """子音なしモーラの総長さ."""
        mora = Mora(
            text="ン",
            consonant=None,
            consonant_length=None,
            vowel="N",
            vowel_length=0.15,
            pitch=5.0,
        )
        assert mora.total_length == pytest.approx(0.15)

    def test_is_voiced_vowel_lowercase(self):
        """小文字母音は有声."""
        mora = Mora(text="ア", vowel="a", vowel_length=0.1, pitch=5.0)
        assert mora.is_voiced_vowel is True

    def test_is_voiced_vowel_uppercase(self):
        """大文字母音は無声."""
        mora = Mora(
            text="ス", consonant="s", consonant_length=0.1,
            vowel="U", vowel_length=0.05, pitch=5.0
        )
        assert mora.is_voiced_vowel is False

    def test_is_voiced_vowel_n(self):
        """撥音Nは有声."""
        mora = Mora(text="ン", vowel="N", vowel_length=0.15, pitch=5.0)
        assert mora.is_voiced_vowel is True


class TestAudioQuery:
    """AudioQueryモデルのテスト."""

    def test_parse_from_dict(self):
        """辞書からのパース."""
        data = {
            "accent_phrases": [
                {
                    "moras": [
                        {
                            "text": "コ",
                            "consonant": "k",
                            "consonant_length": 0.1,
                            "vowel": "o",
                            "vowel_length": 0.15,
                            "pitch": 5.0,
                        }
                    ],
                    "accent": 1,
                    "pause_mora": None,
                    "is_interrogative": False,
                }
            ],
            "speedScale": 1.0,
            "pitchScale": 0.0,
            "intonationScale": 1.0,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.1,
            "postPhonemeLength": 0.1,
            "outputSamplingRate": 24000,
            "outputStereo": False,
        }

        query = AudioQuery.model_validate(data)

        assert len(query.accent_phrases) == 1
        assert len(query.accent_phrases[0].moras) == 1
        assert query.accent_phrases[0].moras[0].text == "コ"
        assert query.speed_scale == 1.0
        assert query.pre_phoneme_length == 0.1

    def test_serialize_to_dict(self):
        """辞書へのシリアライズ（by_alias）."""
        mora = Mora(
            text="コ",
            consonant="k",
            consonant_length=0.1,
            vowel="o",
            vowel_length=0.15,
            pitch=5.0,
        )
        phrase = AccentPhrase(moras=[mora], accent=1)
        query = AudioQuery(accent_phrases=[phrase])

        data = query.model_dump(by_alias=True)

        assert "speedScale" in data
        assert "prePhonemeLength" in data
        assert data["accent_phrases"][0]["moras"][0]["text"] == "コ"
