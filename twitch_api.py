import json
import os
import time

import requests

from config import CLIENT_ID
from config import SCOPES
from config import TOKEN_FILE
from config import TWITCH_API_BASE
from config import TWITCH_DEVICE_URL
from config import TWITCH_TOKEN_URL
from config import TWITCH_VALIDATE_URL


# ============================================================
# Token保存・読み込み
# ============================================================

def load_token():
  if(not os.path.exists(TOKEN_FILE)):
    return None

  try:
    with open(TOKEN_FILE,"r",encoding="utf-8") as f:
      token_data=json.load(f)

    return token_data

  except Exception as e:
    print("Tokenファイル読み込みエラー:")
    print(e)

    return None


def save_token(token_data):
  with open(TOKEN_FILE,"w",encoding="utf-8") as f:
    json.dump(
      token_data,
      f,
      ensure_ascii=False,
      indent=2
    )


def delete_token():
  if(os.path.exists(TOKEN_FILE)):
    os.remove(TOKEN_FILE)


# ============================================================
# Token検証
# ============================================================

def validate_token(access_token):
  headers={
    "Authorization":f"OAuth {access_token}"
  }

  try:
    response=requests.get(
      TWITCH_VALIDATE_URL,
      headers=headers,
      timeout=10
    )

  except requests.RequestException as e:
    raise RuntimeError(
      f"Twitchへの接続に失敗しました。\n{e}"
    )

  if(response.status_code==200):
    return response.json()

  if(response.status_code==401):
    return None

  raise RuntimeError(
    "Token検証中にエラーが発生しました。\n"
    f"HTTP {response.status_code}\n"
    f"{response.text}"
  )


# ============================================================
# Token更新
# ============================================================

def refresh_access_token(refresh_token):
  data={
    "client_id":CLIENT_ID,
    "grant_type":"refresh_token",
    "refresh_token":refresh_token
  }

  try:
    response=requests.post(
      TWITCH_TOKEN_URL,
      data=data,
      timeout=10
    )

  except requests.RequestException as e:
    raise RuntimeError(
      f"Token更新中に通信エラーが発生しました。\n{e}"
    )

  if(response.status_code!=200):
    return None

  token_data=response.json()

  save_token(
    token_data
  )

  return token_data


# ============================================================
# Device Code Flow
# ============================================================

def request_device_code():
  data={
    "client_id":CLIENT_ID,
    "scopes":" ".join(SCOPES)
  }

  try:
    response=requests.post(
      TWITCH_DEVICE_URL,
      data=data,
      timeout=10
    )

  except requests.RequestException as e:
    raise RuntimeError(
      f"認証開始中に通信エラーが発生しました。\n{e}"
    )

  if(response.status_code!=200):
    raise RuntimeError(
      "Twitch認証を開始できませんでした。\n"
      f"HTTP {response.status_code}\n"
      f"{response.text}"
    )

  return response.json()


def poll_device_token(
  device_data,
  status_callback=None
):
  device_code=device_data["device_code"]
  expires_in=device_data["expires_in"]

  interval=device_data.get(
    "interval",
    5
  )

  start_time=time.time()

  while(time.time()-start_time<expires_in):
    data={
      "client_id":CLIENT_ID,
      "scopes":" ".join(SCOPES),
      "device_code":device_code,
      "grant_type":"urn:ietf:params:oauth:grant-type:device_code"
    }

    try:
      response=requests.post(
        TWITCH_TOKEN_URL,
        data=data,
        timeout=10
      )

    except requests.RequestException:
      time.sleep(
        interval
      )

      continue

    if(response.status_code==200):
      token_data=response.json()

      save_token(
        token_data
      )

      return token_data

    try:
      error_data=response.json()

      message=error_data.get(
        "message",
        ""
      )

    except Exception:
      message=""

    if(message=="authorization_pending"):
      if(status_callback is not None):
        status_callback(
          "Twitchでの認証完了を待っています..."
        )

      time.sleep(
        interval
      )

      continue

    if(message=="slow_down"):
      interval+=1

      time.sleep(
        interval
      )

      continue

    if(message=="expired_token"):
      raise RuntimeError(
        "認証コードの有効期限が切れました。"
      )

    if(message=="access_denied"):
      raise RuntimeError(
        "Twitch認証がキャンセルされました。"
      )

    raise RuntimeError(
      "Twitch認証中にエラーが発生しました。\n"
      f"HTTP {response.status_code}\n"
      f"{response.text}"
    )

  raise RuntimeError(
    "Twitch認証の待機時間を超えました。"
  )


# ============================================================
# 有効なToken取得
# ============================================================

def get_valid_token():
  token_data=load_token()

  if(token_data is None):
    return None,None

  access_token=token_data.get(
    "access_token"
  )

  if(access_token is None):
    return None,None

  validation=validate_token(
    access_token
  )

  if(validation is not None):
    required_scopes=set(
      SCOPES
    )

    current_scopes=set(
      validation.get(
        "scopes",
        []
      )
    )

    if(not required_scopes.issubset(current_scopes)):
      return None,None

    return token_data,validation

  refresh_token=token_data.get(
    "refresh_token"
  )

  if(refresh_token is None):
    return None,None

  new_token_data=refresh_access_token(
    refresh_token
  )

  if(new_token_data is None):
    return None,None

  validation=validate_token(
    new_token_data["access_token"]
  )

  if(validation is None):
    return None,None

  return new_token_data,validation


# ============================================================
# Twitch API共通ヘッダ
# ============================================================

def twitch_headers(access_token):
  return {
    "Authorization":f"Bearer {access_token}",
    "Client-Id":CLIENT_ID,
    "Content-Type":"application/json"
  }


# ============================================================
# 現在の配信情報取得
# ============================================================

def get_channel_info(
  access_token,
  broadcaster_id
):
  url=TWITCH_API_BASE+"/channels"

  params={
    "broadcaster_id":broadcaster_id
  }

  try:
    response=requests.get(
      url,
      headers=twitch_headers(access_token),
      params=params,
      timeout=10
    )

  except requests.RequestException as e:
    raise RuntimeError(
      f"Twitchへの接続に失敗しました。\n{e}"
    )

  if(response.status_code==401):
    raise PermissionError(
      "Access Tokenが無効です。"
    )

  if(response.status_code!=200):
    raise RuntimeError(
      "チャンネル情報を取得できませんでした。\n"
      f"HTTP {response.status_code}\n"
      f"{response.text}"
    )

  data=response.json().get(
    "data",
    []
  )

  if(len(data)==0):
    raise RuntimeError(
      "チャンネル情報が見つかりませんでした。"
    )

  return data[0]


# ============================================================
# カテゴリ検索
# ============================================================

def search_category(
  access_token,
  game_name
):
  url=TWITCH_API_BASE+"/search/categories"

  params={
    "query":game_name,
    "first":100
  }

  try:
    response=requests.get(
      url,
      headers=twitch_headers(access_token),
      params=params,
      timeout=10
    )

  except requests.RequestException as e:
    raise RuntimeError(
      f"Twitchへの接続に失敗しました。\n{e}"
    )

  if(response.status_code==401):
    raise PermissionError(
      "Access Tokenが無効です。"
    )

  if(response.status_code!=200):
    raise RuntimeError(
      "カテゴリ検索に失敗しました。\n"
      f"HTTP {response.status_code}\n"
      f"{response.text}"
    )

  categories=response.json().get(
    "data",
    []
  )

  for category in categories:
    if(category["name"].lower()==game_name.lower()):
      return category

  return None


# ============================================================
# チャンネル情報変更
# ============================================================

def update_channel(
  access_token,
  broadcaster_id,
  title,
  game_id,
  tags
):
  url=TWITCH_API_BASE+"/channels"

  params={
    "broadcaster_id":broadcaster_id
  }

  data={
    "title":title,
    "game_id":game_id,
    "tags":tags
  }

  try:
    response=requests.patch(
      url,
      headers=twitch_headers(access_token),
      params=params,
      json=data,
      timeout=10
    )

  except requests.RequestException as e:
    raise RuntimeError(
      f"Twitchへの接続に失敗しました。\n{e}"
    )

  if(response.status_code==401):
    raise PermissionError(
      "Access Tokenが無効です。"
    )

  if(response.status_code!=204):
    raise RuntimeError(
      "チャンネル情報を変更できませんでした。\n"
      f"HTTP {response.status_code}\n"
      f"{response.text}"
    )