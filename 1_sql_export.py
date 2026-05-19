"""
Stage 1: Database Export

SQL Server から大量データを抽出し、後続の前処理パイプライン
（Stage 2〜4）で利用するための CSV として分割保存するステージ。

- pyodbc による SQL Server 接続
- pandas による chunksize ストリーミング取得
- 100万行ごとの分割保存
- 再開ポイントの指定が可能
"""

import os
import pyodbc
import pandas as pd


class DatabaseExporter:
    """SQL Server からデータを抽出し、CSV に分割保存するクラス"""

    def __init__(self):
        # ※ 転職用のため、接続情報はダミー値に置換
        self.conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=sample-server.database.windows.net;"
            "DATABASE=sample-database;"
            "UID=sample-user;"
            "PWD=sample-password"
        )

        # 出力フォルダ
        self.output_dir = os.path.join(os.getcwd(), "progressHistoryinfo_source_data")
        os.makedirs(self.output_dir, exist_ok=True)

        # 途中から再開するための SQL（ダミー値）
        self.sql = """
            SELECT *
            FROM dbo.ProgressHistoryInfo
            WHERE ProgressHistoryInfoId >= 100000000
            ORDER BY ProgressHistoryInfoId
        """

        # 1ファイルあたりの行数
        self.chunksize = 1_000_000

        # 再開ファイル番号
        self.start_file_index = 1

    def run(self):
        """SQL を実行し、結果を分割して CSV 保存する"""
        conn = pyodbc.connect(self.conn_str)

        i = self.start_file_index
        for chunk in pd.read_sql(self.sql, conn, chunksize=self.chunksize):
            filename = os.path.join(self.output_dir, f"output_part_{i:03}.csv")
            print(f"Saving {filename} ...")
            chunk.to_csv(filename, index=False)
            i += 1

        print("✔ 全件保存完了")
