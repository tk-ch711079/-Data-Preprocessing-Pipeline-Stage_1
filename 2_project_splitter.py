"""
Stage 2: Project-based CSV Splitter

Stage 1 で抽出した大量 CSV を、ProjectId 単位で統合・重複排除し、
後続の Stage 3（Excel 集約）で扱いやすい形に分割保存するステージ。

主な処理内容：
- GUI（PySide6）で最大5つの CSV を指定可能
- 指定がなければ source ディレクトリ内の全 CSV を処理
- ProjectId ごとにデータをグルーピング
- 既存の分割ファイル（pj_{projectId}_*.csv）を読み込み統合
- 主キー ProgressHistoryInfoId で重複排除
- EquipmentId → WorkId でソート
- 100万行ごとに分割保存
"""

import os
import glob
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)

SOURCE_DIR = "progressHistoryinfo_source_data"
OUTPUT_DIR = "progress_ID_division"
MAX_ROWS = 1_000_000


class ProjectSplitter:
    """ProjectId 単位で CSV を統合・分割保存する処理を担当"""

    def __init__(self):
        os.makedirs(SOURCE_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def load_existing(self, project_id):
        """既存の pj_{projectId}_*.csv を読み込む"""
        pattern = os.path.join(OUTPUT_DIR, f"pj_{project_id}_*.csv")
        files = sorted(glob.glob(pattern))
        df_list = [pd.read_csv(f) for f in files]
        return df_list, files

    def save_split(self, project_id, df_all):
        """統合済みデータを MAX_ROWS ごとに分割保存"""
        _, existing_files = self.load_existing(project_id)

        # 既存ファイル削除
        for f in existing_files:
            os.remove(f)

        total = len(df_all)
        index = 0
        pos = 0

        while pos < total:
            index += 1
            chunk = df_all.iloc[pos:pos + MAX_ROWS]
            pos += len(chunk)

            rows = len(chunk)
            filename = f"pj_{project_id}_{index}_{rows}.csv"
            chunk.to_csv(os.path.join(OUTPUT_DIR, filename), index=False, encoding="utf-8-sig")

    def process(self, file_paths):
        """CSV を読み込み、ProjectId ごとに統合・分割保存"""
        project_data = {}

        # CSV 読み込み
        for file in file_paths:
            df = pd.read_csv(file)

            if "ProjectId" not in df.columns:
                raise ValueError(f"{file} に ProjectId カラムがありません")

            for pid, group in df.groupby("ProjectId"):
                project_data.setdefault(pid, []).append(group)

        # ProjectId ごとに処理
        for pid, df_list in project_data.items():
            df_new = pd.concat(df_list, ignore_index=True)

            df_exist_list, _ = self.load_existing(pid)
            df_all = pd.concat(df_exist_list + [df_new], ignore_index=True)

            # 主キーで重複排除
            df_all = df_all.drop_duplicates(subset=["ProgressHistoryInfoId"])

            # ソート
            df_all = df_all.sort_values(["EquipmentId", "WorkId"], ignore_index=True)

            # 保存
            self.save_split(pid, df_all)


class FileInputWindow(QWidget):
    """GUI で CSV を最大5つ指定し、ProjectSplitter を実行する"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stage 2: CSV Project Splitter")

        layout = QVBoxLayout()
        self.inputs = []

        # 入力欄 5 個
        for i in range(5):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"ファイル {i+1}: "))
            edit = QLineEdit()
            edit.setPlaceholderText("例: data1 → data1.csv")
            row.addWidget(edit)
            layout.addLayout(row)
            self.inputs.append(edit)

        btn = QPushButton("実行")
        btn.clicked.connect(self.run_process)
        layout.addWidget(btn)

        self.setLayout(layout)

    def run_process(self):
        splitter = ProjectSplitter()

        # 入力されたファイル名を取得
        file_names = [e.text().strip() for e in self.inputs if e.text().strip()]

        if not file_names:
            file_paths = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.csv")))
        else:
            file_paths = [
                os.path.join(SOURCE_DIR, f"{name}.csv" if not name.endswith(".csv") else name)
                for name in file_names
            ]

        try:
            splitter.process(file_paths)
            QMessageBox.information(self, "完了", "処理が完了しました")
        except Exception as e:
            QMessageBox.critical(self, "エラー", str(e))


if __name__ == "__main__":
    app = QApplication([])
    window = FileInputWindow()
    window.show()
    app.exec()
