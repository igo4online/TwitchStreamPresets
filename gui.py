import threading
import webbrowser
import tkinter as tk

from tkinter import messagebox
from tkinter import ttk

from presets import load_presets
from presets import save_presets

from twitch_api import get_channel_info
from twitch_api import get_valid_token
from twitch_api import poll_device_token
from twitch_api import request_device_code
from twitch_api import search_category
from twitch_api import update_channel
from twitch_api import validate_token


# ============================================================
# プリセット編集ウィンドウ
# ============================================================

class PresetEditor:

  def __init__(
    self,
    parent,
    presets,
    save_callback,
    resolve_category_callback
  ):
    self.parent=parent
    self.presets=presets
    self.save_callback=save_callback
    self.resolve_category_callback=resolve_category_callback

    self.selected_name=None
    self.original_game=None
    self.original_game_id=None

    self.window=tk.Toplevel(
      parent
    )

    self.window.title(
      "プリセット編集 / Edit Presets"
    )

    self.window.geometry(
      "820x520"
    )

    self.window.transient(
      parent
    )

    self.create_widgets()

    self.refresh_list()


  # ----------------------------------------------------------
  # GUI生成
  # ----------------------------------------------------------

  def create_widgets(self):
    main_frame=ttk.Frame(
      self.window,
      padding=10
    )

    main_frame.pack(
      fill="both",
      expand=True
    )

    # --------------------------------------------------------
    # 左側：プリセット一覧
    # --------------------------------------------------------

    left_frame=ttk.LabelFrame(
      main_frame,
      text="プリセット一覧 / Presets",
      padding=10
    )

    left_frame.pack(
      side="left",
      fill="both",
      padx=(0,10)
    )

    self.listbox=tk.Listbox(
      left_frame,
      width=28
    )

    self.listbox.pack(
      fill="both",
      expand=True
    )

    self.listbox.bind(
      "<<ListboxSelect>>",
      self.on_select
    )

    # --------------------------------------------------------
    # 表示順変更ボタン
    # --------------------------------------------------------

    order_button_frame=ttk.Frame(
      left_frame
    )

    order_button_frame.pack(
      fill="x",
      pady=(10,0)
    )

    self.move_up_button=ttk.Button(
      order_button_frame,
      text="↑ / Up",
      command=lambda:self.move_selected(-1)
    )

    self.move_up_button.pack(
      side="left",
      expand=True,
      fill="x",
      padx=(0,3)
    )

    self.move_down_button=ttk.Button(
      order_button_frame,
      text="↓ / Down",
      command=lambda:self.move_selected(1)
    )

    self.move_down_button.pack(
      side="left",
      expand=True,
      fill="x",
      padx=(3,0)
    )

    # --------------------------------------------------------
    # 右側：編集
    # --------------------------------------------------------

    right_frame=ttk.LabelFrame(
      main_frame,
      text="編集 / Edit",
      padding=10
    )

    right_frame.pack(
      side="left",
      fill="both",
      expand=True
    )

    # --------------------------------------------------------
    # プリセット名
    # --------------------------------------------------------

    ttk.Label(
      right_frame,
      text="プリセット名 / Preset Name"
    ).pack(
      anchor="w"
    )

    self.name_var=tk.StringVar()

    self.name_entry=ttk.Entry(
      right_frame,
      textvariable=self.name_var
    )

    self.name_entry.pack(
      fill="x",
      pady=(0,10)
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    ttk.Label(
      right_frame,
      text="タイトル / Title"
    ).pack(
      anchor="w"
    )

    self.title_var=tk.StringVar()

    self.title_entry=ttk.Entry(
      right_frame,
      textvariable=self.title_var
    )

    self.title_entry.pack(
      fill="x",
      pady=(0,10)
    )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    ttk.Label(
      right_frame,
      text="カテゴリ / Category"
    ).pack(
      anchor="w"
    )

    self.game_var=tk.StringVar()

    self.game_entry=ttk.Entry(
      right_frame,
      textvariable=self.game_var
    )

    self.game_entry.pack(
      fill="x",
      pady=(0,10)
    )

    # --------------------------------------------------------
    # Tags
    # --------------------------------------------------------

    ttk.Label(
      right_frame,
      text="タグ / Tags（カンマ区切り / comma-separated）"
    ).pack(
      anchor="w"
    )

    self.tags_var=tk.StringVar()

    self.tags_entry=ttk.Entry(
      right_frame,
      textvariable=self.tags_var
    )

    self.tags_entry.pack(
      fill="x",
      pady=(0,20)
    )

    # --------------------------------------------------------
    # 編集ボタン
    # --------------------------------------------------------

    button_frame=ttk.Frame(
      right_frame
    )

    button_frame.pack(
      fill="x"
    )

    self.new_button=ttk.Button(
      button_frame,
      text="新規 / New",
      command=self.clear_form
    )

    self.new_button.pack(
      side="left",
      padx=(0,5)
    )

    self.save_button=ttk.Button(
      button_frame,
      text="保存 / Save",
      command=self.save_current
    )

    self.save_button.pack(
      side="left",
      padx=5
    )

    self.delete_button=ttk.Button(
      button_frame,
      text="削除 / Delete",
      command=self.delete_current
    )

    self.delete_button.pack(
      side="left",
      padx=5
    )

    self.close_button=ttk.Button(
      button_frame,
      text="閉じる / Close",
      command=self.window.destroy
    )

    self.close_button.pack(
      side="right"
    )


  # ----------------------------------------------------------
  # 一覧更新
  # ----------------------------------------------------------

  def refresh_list(
    self,
    select_name=None
  ):
    self.listbox.delete(
      0,
      tk.END
    )

    names=list(
      self.presets.keys()
    )

    for name in names:
      self.listbox.insert(
        tk.END,
        name
      )

    if(select_name is not None):
      if(select_name in names):
        index=names.index(
          select_name
        )

        self.listbox.selection_set(
          index
        )

        self.listbox.see(
          index
        )


  # ----------------------------------------------------------
  # 選択
  # ----------------------------------------------------------

  def on_select(
    self,
    event=None
  ):
    selection=self.listbox.curselection()

    if(len(selection)==0):
      return

    index=selection[0]

    name=self.listbox.get(
      index
    )

    if(name not in self.presets):
      return

    preset=self.presets[
      name
    ]

    self.selected_name=name

    self.original_game=preset.get(
      "game",
      ""
    )

    self.original_game_id=preset.get(
      "game_id",
      ""
    )

    self.name_var.set(
      name
    )

    self.title_var.set(
      preset.get(
        "title",
        ""
      )
    )

    self.game_var.set(
      self.original_game
    )

    self.tags_var.set(
      ", ".join(
        preset.get(
          "tags",
          []
        )
      )
    )

  # ----------------------------------------------------------
  # 表示順変更
  # ----------------------------------------------------------

  def move_selected(
    self,
    direction
  ):
    selection=self.listbox.curselection()

    if(len(selection)==0):
      return

    current_index=selection[0]

    names=list(
      self.presets.keys()
    )

    new_index=current_index+direction

    if(new_index<0):
      return

    if(new_index>=len(names)):
      return

    current_name=names[
      current_index
    ]

    items=list(
      self.presets.items()
    )

    items[
      current_index
    ],items[
      new_index
    ]=items[
      new_index
    ],items[
      current_index
    ]

    # self.presets自体は置き換えず、中身だけ並べ替える。
    # これによりメイン画面側と同じdictオブジェクトを維持する。
    self.presets.clear()

    self.presets.update(
      items
    )

    save_presets(
      self.presets
    )

    self.refresh_list(
      select_name=current_name
    )

    self.save_callback()


  # ----------------------------------------------------------
  # 新規
  # ----------------------------------------------------------

  def clear_form(self):
    self.selected_name=None
    self.original_game=None
    self.original_game_id=None

    self.listbox.selection_clear(
      0,
      tk.END
    )

    self.name_var.set("")
    self.title_var.set("")
    self.game_var.set("")
    self.tags_var.set("")

    self.name_entry.focus_set()


  # ----------------------------------------------------------
  # 保存
  # ----------------------------------------------------------

  def save_current(self):
    name=self.name_var.get().strip()
    title=self.title_var.get().strip()
    game=self.game_var.get().strip()

    tags=[
      tag.strip()
      for tag in self.tags_var.get().split(",")
      if(tag.strip()!="")
    ]

    if(name==""):
      messagebox.showwarning(
        "入力エラー / Input Error",
        "プリセット名を入力してください。\n"
        "Please enter a preset name.",
        parent=self.window
      )

      return

    if(title==""):
      messagebox.showwarning(
        "入力エラー / Input Error",
        "タイトルを入力してください。\n"
        "Please enter a title.",
        parent=self.window
      )

      return

    if(game==""):
      messagebox.showwarning(
        "入力エラー / Input Error",
        "カテゴリを入力してください。\n"
        "Please enter a category.",
        parent=self.window
      )

      return

    # --------------------------------------------------------
    # CategoryとGame IDを決定
    #
    # Categoryが変更されておらず、
    # 既存のgame_idがある場合はAPI検索を省略する。
    # --------------------------------------------------------

    if(
      self.selected_name is not None
      and
      game==self.original_game
      and
      self.original_game_id not in [None,""]
    ):
      canonical_game=game
      game_id=self.original_game_id

    else:
      try:
        category=self.resolve_category_callback(
          game
        )

      except Exception as e:
        messagebox.showerror(
          "カテゴリ検索エラー / Category Search Error",
          "カテゴリの検索に失敗しました。\n"
          "Failed to search for the category.\n\n"
          f"{e}",
          parent=self.window
        )

        return

      if(category is None):
        messagebox.showwarning(
          "カテゴリ未検出 / Category Not Found",
          f"Twitchカテゴリ「{game}」が見つかりませんでした。\n"
          f'The Twitch category "{game}" was not found.',
          parent=self.window
        )

        return

      canonical_game=category[
        "name"
      ]

      game_id=category[
        "id"
      ]

    # --------------------------------------------------------
    # 名前変更
    # --------------------------------------------------------

    if(
      self.selected_name is not None
      and
      self.selected_name!=name
    ):
      if(name in self.presets):
        messagebox.showwarning(
          "名前重複 / Duplicate Name",
          "同じ名前のプリセットが既に存在します。\n"
          "A preset with the same name already exists.",
          parent=self.window
        )

        return

      del self.presets[
        self.selected_name
      ]

    # --------------------------------------------------------
    # 新規作成時の名前重複
    # --------------------------------------------------------

    if(
      self.selected_name is None
      and
      name in self.presets
    ):
      overwrite=messagebox.askyesno(
        "確認 / Confirmation",
        "同じ名前のプリセットが既に存在します。\n"
        "上書きしますか？\n\n"
        "A preset with the same name already exists.\n"
        "Do you want to overwrite it?",
        parent=self.window
      )

      if(not overwrite):
        return

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    self.presets[name]={
      "title":title,
      "game":canonical_game,
      "game_id":game_id,
      "tags":tags
    }

    self.selected_name=name
    self.original_game=canonical_game
    self.original_game_id=game_id

    self.game_var.set(
      canonical_game
    )

    save_presets(
      self.presets
    )

    self.save_callback()

    self.refresh_list(
      select_name=name
    )

    messagebox.showinfo(
      "保存完了 / Saved",
      "プリセットを保存しました。\n"
      "The preset has been saved.",
      parent=self.window
    )


  # ----------------------------------------------------------
  # 削除
  # ----------------------------------------------------------

  def delete_current(self):
    if(self.selected_name is None):
      messagebox.showwarning(
        "削除 / Delete",
        "削除するプリセットを選択してください。\n"
        "Please select a preset to delete.",
        parent=self.window
      )

      return

    name=self.selected_name

    result=messagebox.askyesno(
      "削除確認 / Delete Confirmation",
      f"プリセット「{name}」を削除しますか？\n\n"
      f'Delete the preset "{name}"?',
      parent=self.window
    )

    if(not result):
      return

    if(name in self.presets):
      del self.presets[
        name
      ]

    save_presets(
      self.presets
    )

    self.clear_form()

    self.refresh_list()

    self.save_callback()


# ============================================================
# メインGUI
# ============================================================

class TwitchPresetApp:

  def __init__(
    self,
    root
  ):
    self.root=root

    self.token_data=None
    self.validation=None

    self.access_token=None
    self.broadcaster_id=None

    self.presets=load_presets()

    self.root.title(
      "Twitch Stream Presets v001"
    )

    self.root.geometry(
      "700x590"
    )

    self.create_widgets()

    self.refresh_preset_combo()

    self.root.after(
      100,
      self.check_login_on_start
    )


  # ----------------------------------------------------------
  # GUI生成
  # ----------------------------------------------------------

  def create_widgets(self):
    main_frame=ttk.Frame(
      self.root,
      padding=15
    )

    main_frame.pack(
      fill="both",
      expand=True
    )

    # --------------------------------------------------------
    # Twitch接続状態
    # --------------------------------------------------------

    account_frame=ttk.LabelFrame(
      main_frame,
      text="Twitchアカウント / Twitch Account",
      padding=10
    )

    account_frame.pack(
      fill="x",
      pady=(0,10)
    )

    self.account_label=ttk.Label(
      account_frame,
      text="確認中... / Checking..."
    )

    self.account_label.pack(
      side="left"
    )

    self.login_button=ttk.Button(
      account_frame,
      text="Twitchに接続 / Connect to Twitch",
      command=self.start_login
    )

    self.login_button.pack(
      side="right"
    )

    # --------------------------------------------------------
    # プリセット
    # --------------------------------------------------------

    preset_frame=ttk.LabelFrame(
      main_frame,
      text="プリセット / Preset",
      padding=10
    )

    preset_frame.pack(
      fill="x",
      pady=(0,10)
    )

    preset_select_frame=ttk.Frame(
      preset_frame
    )

    preset_select_frame.pack(
      fill="x"
    )

    self.preset_var=tk.StringVar()

    self.preset_combo=ttk.Combobox(
      preset_select_frame,
      textvariable=self.preset_var,
      state="readonly"
    )

    self.preset_combo.pack(
      side="left",
      fill="x",
      expand=True,
      padx=(0,5)
    )

    self.preset_combo.bind(
      "<<ComboboxSelected>>",
      self.on_preset_selected
    )

    self.edit_preset_button=ttk.Button(
      preset_select_frame,
      text="プリセット編集 / Edit Presets",
      command=self.open_preset_editor
    )

    self.edit_preset_button.pack(
      side="right"
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    ttk.Label(
      main_frame,
      text="タイトル / Title"
    ).pack(
      anchor="w"
    )

    self.title_var=tk.StringVar()

    self.title_entry=ttk.Entry(
      main_frame,
      textvariable=self.title_var
    )

    self.title_entry.pack(
      fill="x",
      pady=(0,10)
    )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    ttk.Label(
      main_frame,
      text="カテゴリ / Category"
    ).pack(
      anchor="w"
    )

    self.game_var=tk.StringVar()

    self.game_entry=ttk.Entry(
      main_frame,
      textvariable=self.game_var
    )

    self.game_entry.pack(
      fill="x",
      pady=(0,10)
    )

    # --------------------------------------------------------
    # Tags
    # --------------------------------------------------------

    ttk.Label(
      main_frame,
      text="タグ / Tags（カンマ区切り / comma-separated）"
    ).pack(
      anchor="w"
    )

    self.tags_var=tk.StringVar()

    self.tags_entry=ttk.Entry(
      main_frame,
      textvariable=self.tags_var
    )

    self.tags_entry.pack(
      fill="x",
      pady=(0,15)
    )

    # --------------------------------------------------------
    # APIボタン
    # --------------------------------------------------------

    button_frame=ttk.Frame(
      main_frame
    )

    button_frame.pack(
      fill="x",
      pady=(0,15)
    )

    self.get_button=ttk.Button(
      button_frame,
      text="現在の設定を取得 / Get Current Settings",
      command=self.get_current_settings
    )

    self.get_button.pack(
      side="left",
      expand=True,
      fill="x",
      padx=(0,5)
    )

    self.apply_button=ttk.Button(
      button_frame,
      text="Twitchへ適用 / Apply to Twitch",
      command=self.apply_settings
    )

    self.apply_button.pack(
      side="left",
      expand=True,
      fill="x",
      padx=(5,0)
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status_frame=ttk.LabelFrame(
      main_frame,
      text="状態 / Status",
      padding=10
    )

    status_frame.pack(
      fill="both",
      expand=True
    )

    self.status_var=tk.StringVar(
      value="起動中... / Starting..."
    )

    self.status_label=ttk.Label(
      status_frame,
      textvariable=self.status_var,
      wraplength=630
    )

    self.status_label.pack(
      anchor="w"
    )


  # ----------------------------------------------------------
  # プリセット一覧更新
  # ----------------------------------------------------------

  def refresh_preset_combo(self):
    names=list(
      self.presets.keys()
    )

    current=self.preset_var.get()

    self.preset_combo[
      "values"
    ]=names

    if(len(names)==0):
      self.preset_var.set("")

      self.title_var.set("")
      self.game_var.set("")
      self.tags_var.set("")

      return

    if(current in names):
      self.preset_var.set(
        current
      )

    else:
      self.preset_var.set(
        names[0]
      )

      self.on_preset_selected()


  # ----------------------------------------------------------
  # プリセット編集
  # ----------------------------------------------------------

  def open_preset_editor(self):
    PresetEditor(
      self.root,
      self.presets,
      self.on_presets_changed,
      self.resolve_category
    )


  def on_presets_changed(self):
    self.refresh_preset_combo()


  # ----------------------------------------------------------
  # Category検索
  # ----------------------------------------------------------

  def resolve_category(
    self,
    game_name
  ):
    if(self.access_token is None):
      raise RuntimeError(
        "カテゴリを確認するには、先にTwitchアカウントへ接続してください。\n"
        "Please connect your Twitch account before checking the category."
      )

    category=search_category(
      self.access_token,
      game_name
    )

    return category


  # ----------------------------------------------------------
  # GUI状態更新
  # ----------------------------------------------------------

  def set_status(
    self,
    text
  ):
    self.root.after(
      0,
      lambda:self.status_var.set(
        text
      )
    )


  def set_account_text(
    self,
    text
  ):
    self.root.after(
      0,
      lambda:self.account_label.config(
        text=text
      )
    )


  # ----------------------------------------------------------
  # 起動時Token確認
  # ----------------------------------------------------------

  def check_login_on_start(self):
    thread=threading.Thread(
      target=self.check_login_worker,
      daemon=True
    )

    thread.start()


  def check_login_worker(self):
    try:
      self.set_status(
        "Twitch認証情報を確認しています... / Checking Twitch authentication..."
      )

      token_data,validation=get_valid_token()

      if(token_data is None):
        self.token_data=None
        self.validation=None

        self.access_token=None
        self.broadcaster_id=None

        self.set_account_text(
          "未接続 / Not connected"
        )

        self.set_status(
          "Twitchアカウントに接続してください。 / Please connect your Twitch account."
        )

        return

      self.set_logged_in(
        token_data,
        validation
      )

      self.set_status(
        "Twitchに接続しました。 / Connected to Twitch."
      )

    except Exception as e:
      self.set_account_text(
        "接続エラー / Connection error"
      )

      self.set_status(
        "Twitchへの接続確認中にエラーが発生しました。\n"
        "An error occurred while checking the Twitch connection.\n"
        f"{e}"
      )


  # ----------------------------------------------------------
  # ログイン済み状態
  # ----------------------------------------------------------

  def set_logged_in(
    self,
    token_data,
    validation
  ):
    self.token_data=token_data
    self.validation=validation

    self.access_token=token_data[
      "access_token"
    ]

    self.broadcaster_id=validation[
      "user_id"
    ]

    login=validation.get(
      "login",
      "Unknown"
    )

    self.set_account_text(
      f"接続中 / Connected: {login}"
    )


  # ----------------------------------------------------------
  # Device Code Login
  # ----------------------------------------------------------

  def start_login(self):
    thread=threading.Thread(
      target=self.login_worker,
      daemon=True
    )

    thread.start()


  def login_worker(self):
    try:
      self.set_status(
        "Twitch認証を開始しています... / Starting Twitch authentication..."
      )

      device_data=request_device_code()

      user_code=device_data[
        "user_code"
      ]

      verification_uri=device_data[
        "verification_uri"
      ]

      self.root.after(
        0,
        lambda:self.show_device_code_dialog(
          user_code,
          verification_uri
        )
      )

      token_data=poll_device_token(
        device_data,
        self.set_status
      )

      validation=validate_token(
        token_data["access_token"]
      )

      if(validation is None):
        raise RuntimeError(
          "取得したTokenを検証できませんでした。\n"
          "The obtained token could not be validated."
        )

      self.set_logged_in(
        token_data,
        validation
      )

      self.set_status(
        "Twitch認証が完了しました。 / Twitch authentication completed."
      )

      self.root.after(
        0,
        lambda:messagebox.showinfo(
          "認証完了 / Authentication Complete",
          "Twitchアカウントとの接続が完了しました。\n"
          "Your Twitch account has been connected."
        )
      )

    except Exception as e:
      error_message=str(e)

      self.set_status(
        "Twitch認証中にエラーが発生しました。\n"
        "An error occurred during Twitch authentication.\n"
        f"{error_message}"
      )

      self.root.after(
        0,
        lambda:messagebox.showerror(
          "認証エラー / Authentication Error",
          "Twitch認証に失敗しました。\n"
          "Twitch authentication failed.\n\n"
          f"{error_message}"
        )
      )


  def show_device_code_dialog(
    self,
    user_code,
    verification_uri
  ):
    message=(
      "ブラウザでTwitch認証を行います。\n"
      "Twitch authentication will be performed in your browser.\n\n"
      f"認証コード / Verification Code:\n{user_code}\n\n"
      "OKを押すとブラウザを開きます。\n"
      "Click OK to open your browser."
    )

    messagebox.showinfo(
      "Twitch認証 / Twitch Authentication",
      message
    )

    webbrowser.open(
      verification_uri
    )


  # ----------------------------------------------------------
  # プリセット選択
  # ----------------------------------------------------------

  def on_preset_selected(
    self,
    event=None
  ):
    preset_name=self.preset_var.get()

    if(preset_name not in self.presets):
      return

    preset=self.presets[
      preset_name
    ]

    self.title_var.set(
      preset.get(
        "title",
        ""
      )
    )

    self.game_var.set(
      preset.get(
        "game",
        ""
      )
    )

    self.tags_var.set(
      ", ".join(
        preset.get(
          "tags",
          []
        )
      )
    )


  # ----------------------------------------------------------
  # 現在設定取得
  # ----------------------------------------------------------

  def get_current_settings(self):
    if(self.access_token is None):
      messagebox.showwarning(
        "未接続 / Not Connected",
        "先にTwitchアカウントへ接続してください。\n"
        "Please connect your Twitch account first."
      )

      return

    # プリセットとの対応を解除
    self.preset_var.set("")
    self.preset_combo.selection_clear()

    thread=threading.Thread(
      target=self.get_current_settings_worker,
      daemon=True
    )

    thread.start()


  def get_current_settings_worker(self):
    try:
      self.set_status(
        "現在の配信設定を取得しています... / Getting current stream settings..."
      )

      info=get_channel_info(
        self.access_token,
        self.broadcaster_id
      )

      self.root.after(
        0,
        lambda:self.display_channel_info(
          info
        )
      )

      self.set_status(
        "現在の配信設定を取得しました。 / Current stream settings retrieved."
      )

    except PermissionError:
      self.set_status(
        "Tokenが無効になっています。再接続してください。 / "
        "The token is invalid. Please reconnect."
      )

      self.root.after(
        0,
        lambda:messagebox.showwarning(
          "再認証が必要です / Reauthentication Required",
          "Twitch認証が無効になっています。\n"
          "Twitchに再接続してください。\n\n"
          "Your Twitch authentication is no longer valid.\n"
          "Please reconnect to Twitch."
        )
      )

    except Exception as e:
      error_message=str(e)

      self.set_status(
        "配信設定の取得中にエラーが発生しました。\n"
        "An error occurred while retrieving the stream settings.\n"
        f"{error_message}"
      )

      self.root.after(
        0,
        lambda:messagebox.showerror(
          "取得エラー / Retrieval Error",
          "現在の配信設定を取得できませんでした。\n"
          "Failed to retrieve the current stream settings.\n\n"
          f"{error_message}"
        )
      )


  def display_channel_info(
    self,
    info
  ):
    self.title_var.set(
      info.get(
        "title",
        ""
      )
    )

    self.game_var.set(
      info.get(
        "game_name",
        ""
      )
    )

    self.tags_var.set(
      ", ".join(
        info.get(
          "tags",
          []
        )
      )
    )


  # ----------------------------------------------------------
  # Twitchへ適用
  # ----------------------------------------------------------

  def apply_settings(self):
    if(self.access_token is None):
      messagebox.showwarning(
        "未接続 / Not Connected",
        "先にTwitchアカウントへ接続してください。\n"
        "Please connect your Twitch account first."
      )

      return

    title=self.title_var.get().strip()
    game_name=self.game_var.get().strip()

    tags=[
      tag.strip()
      for tag in self.tags_var.get().split(",")
      if(tag.strip()!="")
    ]

    if(title==""):
      messagebox.showwarning(
        "入力エラー / Input Error",
        "タイトルを入力してください。\n"
        "Please enter a title."
      )

      return

    if(game_name==""):
      messagebox.showwarning(
        "入力エラー / Input Error",
        "カテゴリを入力してください。\n"
        "Please enter a category."
      )

      return

    # --------------------------------------------------------
    # 現在選択されているプリセットとCategoryが一致する場合、
    # 保存済みgame_idを利用する。
    # --------------------------------------------------------

    preset_name=self.preset_var.get()

    game_id=""

    if(preset_name in self.presets):
      preset=self.presets[
        preset_name
      ]

      preset_game=preset.get(
        "game",
        ""
      )

      if(preset_game==game_name):
        game_id=preset.get(
          "game_id",
          ""
        )

    thread=threading.Thread(
      target=self.apply_settings_worker,
      args=(
        title,
        game_name,
        game_id,
        tags,
        preset_name
      ),
      daemon=True
    )

    thread.start()


  def apply_settings_worker(
    self,
    title,
    game_name,
    game_id,
    tags,
    preset_name
  ):
    try:
      # ------------------------------------------------------
      # game_idが保存されていない場合のみ検索
      # ------------------------------------------------------

      if(game_id==""):
        self.set_status(
          f"カテゴリ「{game_name}」を検索しています... / "
          f'Searching for category "{game_name}"...'
        )

        category=search_category(
          self.access_token,
          game_name
        )

        if(category is None):
          raise RuntimeError(
            f"Twitchカテゴリ「{game_name}」が見つかりませんでした。\n"
            f'The Twitch category "{game_name}" was not found.'
          )

        game_name=category[
          "name"
        ]

        game_id=category[
          "id"
        ]

        # ----------------------------------------------------
        # 選択中プリセットが該当する場合、
        # game_idを自動保存
        # ----------------------------------------------------

        if(preset_name in self.presets):
          preset=self.presets[
            preset_name
          ]

          if(
            preset.get(
              "game",
              ""
            )==game_name
          ):
            preset[
              "game_id"
            ]=game_id

            save_presets(
              self.presets
            )

      self.set_status(
        "Twitchへ設定を適用しています... / Applying settings to Twitch..."
      )

      update_channel(
        self.access_token,
        self.broadcaster_id,
        title,
        game_id,
        tags
      )

      self.set_status(
        "Twitchへの設定変更が完了しました。 / Settings applied to Twitch."
      )

      self.root.after(
        0,
        lambda:messagebox.showinfo(
          "完了 / Complete",
          "Twitchの配信設定を変更しました。\n"
          "The Twitch stream settings have been updated.\n\n"
          f"タイトル / Title:\n{title}\n\n"
          f"カテゴリ / Category:\n{game_name}\n\n"
          f"タグ / Tags:\n{', '.join(tags)}"
        )
      )

    except PermissionError:
      self.set_status(
        "Tokenが無効になっています。 / The token is invalid."
      )

      self.root.after(
        0,
        lambda:messagebox.showwarning(
          "再認証が必要です / Reauthentication Required",
          "Twitch認証が無効になっています。\n"
          "Twitchに再接続してください。\n\n"
          "Your Twitch authentication is no longer valid.\n"
          "Please reconnect to Twitch."
        )
      )

    except Exception as e:
      error_message=str(e)

      self.set_status(
        "設定変更中にエラーが発生しました。\n"
        "An error occurred while applying the settings.\n"
        f"{error_message}"
      )

      self.root.after(
        0,
        lambda:messagebox.showerror(
          "変更エラー / Update Error",
          "Twitchの配信設定を変更できませんでした。\n"
          "Failed to update the Twitch stream settings.\n\n"
          f"{error_message}"
        )
      )