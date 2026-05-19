# Data Preprocessing Pipeline (Stage 1–3)

本リポジトリは、業務システムから出力される大量データを
「抽出 → 分割統合 → マスタ変換」するための
データ前処理パイプライン（Stage1〜3）をまとめたものです。

数百万〜数千万レコード規模のデータを扱うことを前提に設計しており、
SQL Server からの段階的抽出、ProjectId 単位での分割統合、
変換マスタによるファイル名・進捗記号の正規化を自動化しています。

このパイプラインは、後続の分析処理や Excel 集約処理（Stage4）に
渡すための「データ品質を整える基盤レイヤー」を担っています。

---

## 📌 Stage 構成

### 1：Database Export**
- SQL Server から大量データを chunksize でストリーミング抽出  
- 100万行ごとに CSV 分割保存  
- 再開ポイント指定に対応  
- `stage1_sql_export.py`

### 2：Project-based CSV Splitter**
- ProjectId ごとにデータを自動分割  
- 既存データとの統合・重複排除  
- EquipmentId → WorkId でソート  
- PySide6 GUI で最大5ファイル指定可能  
- `stage2_project_splitter.py`

### 3：Master-based File & Value Converter**
- 変換マスタ（変換マスタ.csv）によるファイル名変換  
- ProgressDiv / ResultProgressDiv の記号変換  
- Windows 長パス対応  
- `stage3_master_converter.py`

---

## 📁 ファイル構成

├── 1_sql_export.py
├── 2_project_splitter.py
├── 3_master_converter.py
└── README.md



---

## 🛠 使用技術
- Python 3.x  
- pandas  
- pyodbc  
- PySide6  
- Windows 長パス対応  

---

## 📄 ライセンス
本リポジトリは転職用のサンプルとして公開しています。
実際の業務データ・接続情報は含まれていません。

