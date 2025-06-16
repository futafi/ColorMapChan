# テストデータファイル説明

このディレクトリには、カラープロットちゃんの3つのファイル形式に対応するテスト用データファイルが含まれています。

## ファイル一覧

### 1. test_plain_csv.csv
- **形式**: PlainCSV（標準CSV）
- **データサイズ**: 25行 × 6列
- **内容**: MOSFET特性測定データ（VG1, VG2の2次元スイープ）
- **用途**: 基本的な2次元ヒートマップ表示テスト

### 2. test_parameter_csv.csv  
- **形式**: ParameterCSV（B1500Atext2csv）
- **データサイズ**: 36行 × 7列（データ部分）
- **内容**: 詳細な測定パラメータ情報付きMOSFET特性データ
- **用途**: メタデータ解析、複雑なデータ構造の処理テスト

### 3. test_analysis_csv.csv
- **形式**: AnalysisCSV（B1500aSingleFileCSV）
- **データサイズ**: 36行 × 9列（データ部分）
- **内容**: AutoAnalysis設定付きMOSFET特性データ
- **用途**: 最新形式の解析、高機能データ処理テスト

## データ特徴

### 共通パラメータ
- **VG1**: ゲート電圧1（-2.0V ～ -1.0V、0.2Vステップ）
- **VG2**: ゲート電圧2（-2.0V ～ -1.0V、0.2Vステップ）  
- **VD**: ドレイン電圧（固定 -0.1V）
- **ID**: ドレイン電流（1pA ～ 1nA範囲）
- **IG1, IG2**: ゲートリーク電流
- **IS**: ソース電流

### 測定条件
- **温度**: 室温（300K想定）
- **測定方式**: 2次元電圧スイープ
- **電流範囲**: pAオーダー（低温動作特性）

## 使用方法

### 開発時テスト
```python
# PlainCSV形式テスト
loader = PlainCSVDataLoader('test_data/test_plain_csv.csv')
df = loader.load_all_data()

# ParameterCSV形式テスト  
loader = ParameterCSVDataLoader('test_data/test_parameter_csv.csv')
df = loader.load_all_data()

# AnalysisCSV形式テスト
loader = AnalysisCSVDataLoader('test_data/test_analysis_csv.csv')
df = loader.load_all_data()

# 自動判別テスト
loader = DataLoaderFactory.create_data_loader('test_data/test_plain_csv.csv')
```

### 表示確認
- **X軸**: VG1 または VG2
- **Y軸**: VG2 または VG1  
- **カラー値**: ID（ドレイン電流）
- **フィルタ**: VD = -0.1V（固定）

## 期待される結果

### ヒートマップ表示
- 右上に向かって電流値が増加するパターン
- 科学記法での電流値表示（1E-12 ～ 1E-09）
- 対数スケールでのカラーマップ表示推奨

### フィルタリング
- VD値でのフィルタリング動作確認
- 数値範囲での絞り込み機能テスト

### 断面プロット
- 任意のVG1値での1次元断面表示
- 任意のVG2値での1次元断面表示

## ファイルサイズ
- test_plain_csv.csv: 約1KB
- test_parameter_csv.csv: 約3KB  
- test_analysis_csv.csv: 約4KB

すべて軽量で高速な開発・テストが可能です。