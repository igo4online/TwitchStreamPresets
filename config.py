import os
import sys


# ============================================================
# アプリ設定
# ============================================================

APP_NAME="TwitchStreamPresets_igo_v001"

CLIENT_ID="314dzyt5ycf8tm91gv9vkf1ipn2c8p"

SCOPES=[
  "channel:manage:broadcast"
]


# ============================================================
# Twitch URL
# ============================================================

TWITCH_DEVICE_URL="https://id.twitch.tv/oauth2/device"
TWITCH_TOKEN_URL="https://id.twitch.tv/oauth2/token"
TWITCH_VALIDATE_URL="https://id.twitch.tv/oauth2/validate"

TWITCH_API_BASE="https://api.twitch.tv/helix"


# ============================================================
# ファイル保存先
#
# Python実行時:
#   .pyファイルと同じディレクトリ
#
# PyInstaller実行時:
#   .exeファイルと同じディレクトリ
# ============================================================

if(getattr(sys,"frozen",False)):
  BASE_DIR=os.path.dirname(
    sys.executable
  )
else:
  BASE_DIR=os.path.dirname(
    os.path.abspath(__file__)
  )


TOKEN_FILE=os.path.join(
  BASE_DIR,
  "token.json"
)

PRESET_FILE=os.path.join(
  BASE_DIR,
  "presets.json"
)