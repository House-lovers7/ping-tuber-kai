"""CLIエントリーポイント."""

import argparse
import sys
from pathlib import Path

from .config import settings
from .output.obs_websocket import is_obs_available
from .ui.app import App
from .voicevox.client import VoicevoxClient, VoicevoxError


def check_voicevox() -> bool:
    """VOICEVOX Engineの接続確認.

    Returns:
        bool: 接続可能な場合True
    """
    try:
        with VoicevoxClient() as client:
            return client.is_available()
    except Exception:
        return False


def list_speakers() -> None:
    """話者一覧を表示."""
    try:
        with VoicevoxClient() as client:
            speakers = client.get_speakers()
            print("Available speakers:")
            print("-" * 40)
            for speaker in speakers:
                print(f"\n{speaker.name}:")
                for style in speaker.styles:
                    print(f"  ID {style.id}: {style.name}")
    except VoicevoxError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """メイン関数."""
    parser = argparse.ArgumentParser(
        description="ping-tuber-kai: VOICEVOX母音リップシンクPNGTuber",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--text", "-t",
        type=str,
        help="発話テキスト",
    )

    parser.add_argument(
        "--speaker", "-s",
        type=int,
        default=settings.voicevox_speaker_id,
        help=f"話者ID (default: {settings.voicevox_speaker_id})",
    )

    parser.add_argument(
        "--obs",
        action="store_true",
        help="OBS WebSocket連携を有効化",
    )

    parser.add_argument(
        "--assets",
        type=Path,
        default=None,
        help="口形状アセットディレクトリ",
    )

    parser.add_argument(
        "--list-speakers",
        action="store_true",
        help="話者一覧を表示",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="VOICEVOX Engine接続確認",
    )

    args = parser.parse_args()

    # 話者一覧表示
    if args.list_speakers:
        list_speakers()
        return

    # 接続確認
    if args.check:
        if check_voicevox():
            print(f"VOICEVOX Engine is available at {settings.voicevox_host}")
            sys.exit(0)
        else:
            print(f"VOICEVOX Engine is not available at {settings.voicevox_host}", file=sys.stderr)
            sys.exit(1)

    # OBS確認
    if args.obs and not is_obs_available():
        print("Warning: obsws-python is not installed. OBS integration disabled.")
        print("Install with: uv sync --extra obs")
        args.obs = False

    # VOICEVOX確認
    if not check_voicevox():
        print(f"Error: VOICEVOX Engine is not available at {settings.voicevox_host}")
        print("Please start VOICEVOX Engine first.")
        print("  Docker: docker run --rm -p 50021:50021 voicevox/voicevox_engine:cpu-latest")
        sys.exit(1)

    # テキスト未指定時はインタラクティブモード案内
    if not args.text:
        print("ping-tuber-kai")
        print("=" * 40)
        print(f"Speaker ID: {args.speaker}")
        print(f"OBS integration: {'enabled' if args.obs else 'disabled'}")
        print()
        print("Usage: ping-tuber --text 'こんにちは'")
        print()
        print("Starting window with no audio...")
        args.text = None

    # アプリケーション実行
    try:
        with App(use_obs=args.obs, assets_dir=args.assets) as app:
            app.run(text=args.text, speaker_id=args.speaker)
    except KeyboardInterrupt:
        print("\nInterrupted.")
    except VoicevoxError as e:
        print(f"VOICEVOX Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
