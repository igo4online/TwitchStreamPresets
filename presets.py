import copy
import json
import os

from config import PRESET_FILE


# ============================================================
# 初期プリセット
#
# presets.jsonが存在しない場合にのみ使用
#
# game_idは初回の保存または適用時にTwitch APIから取得する
# ============================================================

DEFAULT_PRESETS={
  "Bぷよ":{
    "title":"Bぷよ対戦会 配信中！",
    "game":"Puyo Puyo",
    "game_id":"",
    "tags":[
      "日本語",
      "English",
      "puyopuyo"
    ]
  },
  "SMM2":{
    "title":"SMM2 コース募集 Viewer levels",
    "game":"Super Mario Maker 2",
    "game_id":"",
    "tags":[
      "日本語",
      "English",
      "視聴者参加"
    ]
  }
}


# ============================================================
# プリセット保存
# ============================================================

def save_presets(presets):
  with open(PRESET_FILE,"w",encoding="utf-8") as f:
    json.dump(
      presets,
      f,
      ensure_ascii=False,
      indent=2
    )


# ============================================================
# プリセット読み込み
# ============================================================

def load_presets():
  if(not os.path.exists(PRESET_FILE)):
    presets=copy.deepcopy(
      DEFAULT_PRESETS
    )

    save_presets(
      presets
    )

    return presets

  try:
    with open(PRESET_FILE,"r",encoding="utf-8") as f:
      presets=json.load(f)

    if(not isinstance(presets,dict)):
      raise ValueError(
        "presets.jsonの最上位が辞書形式ではありません。"
      )

    # --------------------------------------------------------
    # 旧形式との互換性
    #
    # game_idが存在しない古いプリセットには空文字を追加する。
    # 実際のIDは保存または適用時に取得する。
    # --------------------------------------------------------

    modified=False

    for preset_name,preset in presets.items():
      if("game_id" not in preset):
        preset["game_id"]=""
        modified=True

    if(modified):
      save_presets(
        presets
      )

    return presets

  except Exception as e:
    raise RuntimeError(
      "presets.jsonの読み込みに失敗しました。\n"
      f"{e}"
    )