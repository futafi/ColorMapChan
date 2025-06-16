# カラープロットちゃん対応ファイル形式仕様書

## 概要

カラープロットちゃんは3つの主要なデータファイル形式に対応しています。これらの形式は主にB1500A半導体パラメータアナライザーで生成される測定データファイルに基づいています。

## 1. PlainCSV形式（標準CSV）

### 形式概要
- 最もシンプルな標準CSV形式
- 1行目：列名（ヘッダー）
- 2行目以降：数値データ

### ファイル構造
```
[列名1], [列名2], [列名3], [列名4], ...
[値1], [値2], [値3], [値4], ...
[値1], [値2], [値3], [値4], ...
...
```

### 具体例
```csv
VG, VTG, VD, ID, IG, IS, ITG
0.3, 1, -0.05, -1.9E-13, 0, 0, 5E-13
0.28, 1, -0.05, 2.0E-14, 0, 0, 5E-13
0.26, 1, -0.05, 1.8E-13, 0, 0, 0
```

### 技術仕様
- 文字エンコーディング: UTF-8
- 区切り文字: カンマ (`,`)
- 数値形式: 科学記法対応（例：`1.5E-13`）
- 欠損値: 空文字列または`NaN`
- ヘッダー: 必須（1行目）

### 実装要件
- `pandas.read_csv()`で直接読み込み可能
- 自動データ型推定（`pd.to_numeric()`使用）

## 2. ParameterCSV形式（B1500Atext2csv）

### 形式概要
- B1500Aパラメータアナライザーのtext2csv出力形式
- ヘッダー部分とデータ部分に分離
- 測定パラメータ情報を含む詳細なメタデータ

### ファイル構造
```
[メタデータセクション]
TestParameter, [キー], [値1], [値2], ...
MetaData, [キー], [値]
AnalysisSetup, [キー], [値]
...

[データセクション]
DataName, [列名1], [列名2], [列名3], ...
DataValue, [値1], [値2], [値3], ...
DataValue, [値1], [値2], [値3], ...
...
```

### 具体例
```
SetupTitle, 2502-IdVgg-Vg
PrimitiveTest, I/V Sweep
TestParameter, Context.MainFrame, B1500A
TestParameter, Channel.UnitType, SMU, SMU, SMU, SMU
TestParameter, Channel.Unit, SMU4:HR, SMU1:HP, SMU2:HR, SMU5:HR
TestParameter, Channel.IName, IS, ID, IG, ITG
TestParameter, Channel.VName, VS, VD, VG, VTG
...
DataName, VTG, VG, VD, ID, IG, IS, ITG, grad
DataValue, 3, 0.3, -0.05, 2.0E-14, 0, 0, 5E-13, 0
DataValue, 2.98, 0.3, -0.05, 2.4E-13, 0, -5E-13, 5E-13, 2.2E-13
```

### 技術仕様
- 文字エンコーディング: UTF-8（BOM付きの場合あり）
- 区切り文字: カンマ (`,`)
- データ開始マーカー: `DataName` 行
- データ行マーカー: `DataValue` で始まる行
- メタデータ形式: `キー, 値1, 値2, ...`

### 実装要件
1. ファイル解析フェーズ:
   - `DataName` 行を検出してデータセクション開始位置を特定
   - 列名を `DataName` 行から抽出（最初の要素を除く）

2. データ抽出フェーズ:
   - `DataValue` で始まる行のみを抽出
   - 各行の最初の要素（`DataValue`）を除いてデータとして処理
   - 空文字列は `0` または `NaN` に変換

3. メタデータ処理:
   - `TestParameter`, `MetaData`, `AnalysisSetup` 行を辞書として保存
   - 測定条件の復元に使用

## 3. AnalysisCSV形式（B1500aSingleFileCSV）

### 形式概要
- B1500Aの別形式のシングルファイルCSV出力形式
- より詳細な測定設定情報を含む
- AutoAnalysis設定を含む高機能形式

### ファイル構造
```
[設定ヘッダーセクション]
Setup title,[タイトル]
Classic test name,[テスト名]
Test date,[日付]
Test time,[時刻]
Device ID,[デバイスID]
...

[測定パラメータセクション]
Channel.UnitType,[値1],[値2],...
Channel.Unit,[値1],[値2],...
...

[自動解析設定セクション]
AutoAnalysis.Marker.Data.StartCondition,
[列名1],[列名2],[列名3],...
[データ行1]
[データ行2]
...
```

### 具体例
```
Setup title,2502-IdVg1-Vg2
Classic test name,"I/V Sweep"
Test date,2025/03/03
Test time,23:29:49
Device ID,DG_RB_Cw100_Gw_130_Gap_130
Count,2
...
Channel.UnitType,SMU,SMU,SMU,SMU,SMU
Channel.Unit,SMU5:HR,SMU1:HP,SMU4:HR,SMU2:HR,SMU3:HR
Channel.IName,IS,ID,IG1,IG2,IB
Channel.VName,VS,VD,VG1,VG2,VB
...
AutoAnalysis.Marker.Data.StartCondition,
VG1,ID,grad,VD,VG2,IS,IG1,IG2,VB,IB
3,-8.5E-14,0,-0.05,3,0,-5.5E-12,4.5E-12,0,5.8E-12
2.98,3.2E-14,1.17E-13,-0.05,3,1E-12,-7.415E-10,7.415E-10,0,5.4E-12
```

### 技術仕様
- 文字エンコーディング: UTF-8
- 区切り文字: カンマ (`,`)
- データ開始マーカー: `AutoAnalysis.Marker.Data.StartCondition,` 行
- 列名行: AutoAnalysisマーカーの直後の行
- 引用符: 値に含まれる場合あり（`"I/V Sweep"`など）

### 実装要件
1. ファイル解析フェーズ:
   - `AutoAnalysis.Marker.Data.StartCondition,` 行を検出
   - その直後の行を列名として解析
   - データセクション開始位置を特定

2. ヘッダー解析:
   - AutoAnalysisマーカーより前の行をヘッダーとして処理
   - `キー,値` 形式でメタデータを抽出

3. データ抽出:
   - 列名行の次の行からデータとして処理
   - 空文字列は `NaN` に変換
   - 引用符で囲まれた値の適切な処理

## 自動判別アルゴリズム

### 判別順序
1. ParameterCSV形式の判別:
   - `DataName` 行の存在を確認
   - `DataValue` 行の存在を確認

2. AnalysisCSV形式の判別:
   - `AutoAnalysis.Marker.Data.StartCondition,` 行の存在を確認
   - AutoAnalysis後の列名行の存在を確認

3. PlainCSV形式の判別:
   - 上記2つに該当しない場合
   - 1行目が列名、2行目以降がデータの標準CSV形式として処理

### 実装パターン
```python
def detect_format(file_path):
    try:
        # ParameterCSVを試行
        loader = ParameterCSVDataLoader(file_path)
        loader.get_columns()
        return "parameter_csv"
    except:
        pass
    
    try:
        # AnalysisCSVを試行
        loader = AnalysisCSVDataLoader(file_path)
        loader.get_columns()
        return "analysis_csv"
    except:
        pass
    
    try:
        # PlainCSVを試行
        loader = PlainCSVDataLoader(file_path)
        loader.get_columns()
        return "plain_csv"
    except:
        raise ValueError("未対応のファイル形式")
```

## 共通データ要件

### 必須列構成
- 最小要件: 3列以上（X軸用、Y軸用、値用）
- 推奨構成: 電圧パラメータ2〜9列 + 電流測定値1〜3列

### データ型
- 数値列: `float64` 精度での処理
- 科学記法: `1.5E-13` 形式の自動解析
- 欠損値: `NaN` として適切に処理
