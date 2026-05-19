"""
Stage 3: Master-based File & Value Converter

Stage 2 で作成した ProjectId 分割 CSV に対して、
変換マスタ（変換マスタ.csv）を用いて以下の処理を行うステージ。

- ファイル名の変換（pj_123 → pj_ABC など）
- CSV 内の ProgressDiv / ResultProgressDiv の記号変換
- Windows 長パス対応
- ファイル名の sanitize（禁止文字 → "_"）

変換マスタの構造：
- 変換前_name / 変換後_name
- 変換前_character / 変換後_character
"""

import os
import re
import pandas as pd

TARGET_FOLDER = "progress_ID_division"
MASTER_FILE = "変換マスタ.csv"


class MasterConverter:
    """変換マスタを用いてファイル名・CSV 内の値を変換するクラス"""

    def __init__(self):
        self.folder_path = os.path.abspath(TARGET_FOLDER)
        self.master_path = os.path.abspath(MASTER_FILE)

    # -----------------------------
    # Utility
    # -----------------------------
    def long_path(self, path):
        """Windows 長パス対応"""
        path = os.path.abspath(path)
        return path if path.startswith("\\\\?\\") else "\\\\?\\" + path

    def sanitize_filename(self, name):
        """Windows 禁止文字を "_" に置換"""
        return re.sub(r'[\\/:*?"<>|]', "_", name)

    # -----------------------------
    # Master Loader
    # -----------------------------
    def load_master(self):
        """変換マスタを読み込み、辞書として返す"""
        df = pd.read_csv(self.long_path(self.master_path), encoding="utf-8-sig")

        name_dict = (
            df[["変換前_name", "変換後_name"]]
            .dropna()
            .set_index("変換前_name")["変換後_name"]
            .to_dict()
        )

        char_dict = (
            df[["変換前_character", "変換後_character"]]
            .dropna()
            .set_index("変換前_character")["変換後_character"]
            .to_dict()
        )

        return name_dict, char_dict

    # -----------------------------
    # File Rename
    # -----------------------------
    def rename_files(self, name_dict):
        """ファイル名の変換（pj_123 → pj_ABC など）"""
        pattern = re.compile(r"(pj_\d+)")

        for filename in os.listdir(self.folder_path):
            if not filename.lower().endswith(".csv"):
                continue

            new_name = filename
            matches = pattern.findall(filename)

            for key in matches:
                if key in name_dict:
                    new_name = new_name.replace(key, name_dict[key])

            new_name = self.sanitize_filename(new_name)

            if new_name != filename:
                old_path = self.long_path(os.path.join(self.folder_path, filename))
                new_path = self.long_path(os.path.join(self.folder_path, new_name))
                os.rename(old_path, new_path)
                print(f"[ファイル名変換] {filename} → {new_name}")

    # -----------------------------
    # CSV Value Converter
    # -----------------------------
    def convert_progress_div(self, char_dict):
        """CSV 内の ProgressDiv / ResultProgressDiv を変換"""
        target_cols = ["ResultProgressDiv", "ProgressDiv"]

        for filename in os.listdir(self.folder_path):
            if not filename.lower().endswith(".csv"):
                continue

            file_path = self.long_path(os.path.join(self.folder_path, filename))
            df = pd.read_csv(file_path, encoding="utf-8-sig")

            for col in target_cols:
                if col not in df.columns:
                    print(f"[警告] {filename} に {col} 列がありません")
                    continue

                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].apply(
                    lambda x: char_dict[x] if (not x.isdigit() and x in char_dict) else x
                )

            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            print(f"[内部変換] {filename} の {target_cols} を変換しました")

    # -----------------------------
    # Main
    # -----------------------------
    def run(self):
        if not os.path.exists(self.master_path):
            print("変換マスタ.csv が見つかりません")
            return

        if not os.path.exists(self.folder_path):
            print(f"{TARGET_FOLDER} フォルダが見つかりません")
            return

        name_dict, char_dict = self.load_master()

        self.rename_files(name_dict)
        self.convert_progress_div(char_dict)

        print("✔ Stage 3 完了")


if __name__ == "__main__":
    MasterConverter().run()
