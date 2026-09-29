# Twitch Stream Presets

Twitchの配信タイトル、カテゴリ、タグを、あらかじめ登録したプリセットから簡単に切り替えるためのデスクトップアプリです。

A desktop application for quickly applying predefined Twitch stream titles, categories, and tags.

---

## Features / 主な機能

- 配信タイトルのプリセット切り替え
- Twitchカテゴリの切り替え
- タグの切り替え
- 現在のTwitch配信設定の取得
- プリセットの追加・編集・削除
- プリセットの表示順変更
- Twitch OAuthによるアカウント認証
- Access Tokenの検証
- Refresh Tokenによる自動更新
- Windows向け実行ファイルの配布

The application supports:

- Stream title presets
- Twitch category presets
- Twitch tag presets
- Retrieving current Twitch stream settings
- Adding, editing, and deleting presets
- Reordering presets
- Twitch OAuth authentication
- Access token validation
- Automatic token refresh
- Standalone Windows executable

---

## Screenshot / スクリーンショット

アプリのメイン画面です。

Main application window:

![Twitch Stream Presets screenshot](Screenshot.png)
---

## Installation / インストール

### Windows executable

Pythonをインストールしていない場合は、GitHub ReleasesからWindows用実行ファイルをダウンロードしてください。

1. Open the Releases page.
2. Download the latest Windows executable.
3. Run the downloaded `.exe` file.
4. Click `Twitchに接続 / Connect to Twitch`.
5. Complete the Twitch authorization process in your browser.
6. Return to the application and select a preset.
7. Click `Twitchへ適用 / Apply to Twitch`.

No Twitch Developer configuration is required for normal users.

---

## First Launch / 初回起動

初回起動時には、Twitchアカウントとの接続が必要です。

`Twitchに接続 / Connect to Twitch` を押すと、ブラウザでTwitchの認証ページが開きます。

Twitch上でこのアプリへのアクセスを許可すると、アプリがUser Access Tokenを取得し、以後のTwitch APIアクセスに使用します。

The application uses Twitch's Device Code OAuth flow.
Users do not need to manually configure a Client ID, Client Secret, or redirect URI.

---

## Twitch Permissions / Twitch権限

このアプリは以下のOAuth scopeを要求します。

```text
channel:manage:broadcast
```

この権限は、Twitchチャンネルの配信情報を変更するために使用されます。

Specifically, this application uses this permission to update:

- Stream title
- Twitch category
- Stream tags

The application does not request unrelated permissions such as chat moderation, subscriptions, or private messages.

---

## Presets / プリセット

プリセットには以下の情報が保存されます。

- Preset name
- Stream title
- Twitch category
- Twitch category ID
- Tags

Example:

```json
{
  "Example Preset":{
    "title":"Example stream title",
    "game":"Just Chatting",
    "game_id":"509658",
    "tags":[
      "English"
    ]
  }
}
```

`game_id` is stored internally to reduce unnecessary Twitch API requests.
Users normally do not need to know or edit the category ID directly.

---

## Local Files / ローカル保存ファイル

実行時に、アプリと同じディレクトリに以下のファイルが作成されます。

```text
token.json
presets.json
```

### token.json

Twitch OAuth authentication information is stored in this file.

It may contain:

- Access Token
- Refresh Token

Do not share this file with other people.

Do not upload this file to GitHub or any public storage.

### presets.json

User-defined preset information is stored in this file.

This file does not normally contain authentication credentials, but it may contain personal stream titles or configuration information.

---

## Security / セキュリティ

This application uses Twitch's Public Client + Device Code Flow.

The application does not contain a Twitch Client Secret.

The Client ID included in the source code is not a secret and may be publicly distributed.

However, the following information must be kept private:

```text
token.json
access_token
refresh_token
```

Each user's Twitch tokens are generated locally after that user authorizes the application.

The developer does not need to receive or manage individual users' Twitch tokens.

---

## Running from Source / ソースコードから実行

Requirements:

- Python 3
- tkinter
- requests

Install `requests` if necessary:

```bash
pip install requests
```

Then run:

```bash
python main.py
```

The following Python files should be placed in the same directory:

```text
main.py
config.py
twitch_api.py
presets.py
gui.py
```

---

## File Structure / ファイル構成

```text
TwitchStreamPresets/
├─ main.py
├─ config.py
├─ twitch_api.py
├─ presets.py
├─ gui.py
├─ presets.json
└─ token.json
```

`presets.json` and `token.json` are generated automatically when needed.

---

## Building the Windows Executable / Windows実行ファイルの作成

PyInstaller can be used to build a standalone executable.

Install PyInstaller:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --onefile --noconsole --name TwitchStreamPresets main.py
```

The resulting executable will be created in:

```text
dist/TwitchStreamPresets.exe
```

---

## Notes about Windows SmartScreen

The downloadable executable may be unsigned.

Windows SmartScreen or antivirus software may display a warning when running an unsigned executable downloaded from the Internet.

This does not necessarily indicate that the application is malicious.

If you are concerned about the executable, you may review the source code and run the application directly from Python instead.

---

## Supported Platforms

Currently tested primarily on:

- Windows

The Python source code is designed to use tkinter and may also work on macOS, but packaged macOS builds should be created and tested separately.

---

## Limitations / 制限事項

- Internet access is required to communicate with Twitch.
- Twitch API behavior may change in the future.
- Twitch category names must match valid Twitch categories.
- OAuth tokens may expire or become invalid if Twitch authorization is revoked.
- In some cases, reauthentication may be required.

---

## Privacy

This application does not intentionally send preset data or Twitch authentication tokens to any server operated by the developer.

Communication is performed directly between the application and Twitch services.

---

## License

See the `LICENSE` file for license information.

---

## Disclaimer

This project is an independent tool and is not affiliated with, endorsed by, or sponsored by Twitch Interactive, Inc.

Twitch and related trademarks are the property of their respective owners.
