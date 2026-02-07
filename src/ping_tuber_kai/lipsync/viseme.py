"""母音→口形状（Viseme）マッピングモジュール."""

from enum import StrEnum


class Viseme(StrEnum):
    """口形状（Viseme）."""

    A = "a"  # あ - 大きく開く
    I = "i"  # い - 横に広げる
    U = "u"  # う - すぼめる
    E = "e"  # え - 少し開く+横
    O = "o"  # お - 丸く開く
    N = "n"  # ん - 軽く閉じ
    CLOSED = "closed"  # 閉じ


# 母音→Visemeマッピング
VOWEL_TO_VISEME: dict[str, Viseme] = {
    # 有声母音（小文字）
    "a": Viseme.A,
    "i": Viseme.I,
    "u": Viseme.U,
    "e": Viseme.E,
    "o": Viseme.O,
    "N": Viseme.N,  # 撥音（ん）
    # 無声母音（大文字）→ 閉じ
    "A": Viseme.CLOSED,
    "I": Viseme.CLOSED,
    "U": Viseme.CLOSED,
    "E": Viseme.CLOSED,
    "O": Viseme.CLOSED,
    # ポーズ
    "pau": Viseme.CLOSED,
}


def get_viseme(phoneme: str, is_vowel: bool = True) -> Viseme:
    """音素からVisemeを取得.

    Args:
        phoneme: 音素文字列
        is_vowel: 母音かどうか

    Returns:
        Viseme: 対応する口形状
    """
    if not is_vowel:
        # 子音・ポーズは閉じ
        return Viseme.CLOSED

    return VOWEL_TO_VISEME.get(phoneme, Viseme.CLOSED)


def get_viseme_image_name(viseme: Viseme) -> str:
    """Visemeに対応する画像ファイル名を取得.

    Args:
        viseme: 口形状

    Returns:
        str: 画像ファイル名（拡張子付き）
    """
    return f"{viseme.value}.png"
