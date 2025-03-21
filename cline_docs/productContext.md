# カラープロットちゃん - プロダクトコンテキスト

## プロジェクトの目的

カラープロットちゃんは、MOSFETの低温動作時に発生するクーロンブロッケード現象を分析するための対話型データ可視化アプリケーションです。研究者が大量の測定データから重要な特徴を効率的に見つけ出し、詳細な分析を行うことを支援します。

## 解決する問題

1. **データの可視化課題**
   - 多次元の電圧パラメータ（VG1, VG2, VB等）と電流（ID）の関係を直感的に理解することが困難
   - 広範囲のデータ（例：-10V～10V）から注目すべき狭い範囲（例：-0.5V～0.5V）を特定するのが難しい
   - 電流値の範囲が広く、適切なスケールでの表示が必要

2. **データ処理の課題**
   - 大量のデータポイント（>10,000点）を効率的に処理する必要がある
   - 複数の電圧パラメータから任意の2つを選んで表示したい
   - 表示していない次元のパラメータ値でデータをフィルタリングしたい

3. **操作性の課題**
   - 関心領域を素早く特定し、詳細な観察を行いたい
   - 表示範囲やカラーマップを柔軟に調整したい
   - データポイントの正確な値を確認したい

## 主な機能

1. **データ表示**
   - 2次元ヒートマップによる電流データの可視化
   - 任意の電圧パラメータを軸として選択可能
   - カラーマップの選択（plasma優先）と調整
   - 線形/対数スケールの切り替え

2. **インタラクティブ操作**
   - マウスドラッグによる関心領域の選択と拡大
   - スライダーによる表示範囲の動的調整
   - リアルタイムのデータ値表示

3. **データ処理**
   - 大規模データの効率的な読み込みと処理
   - 多次元データのフィルタリング
   - データのエクスポート機能

## 期待される効果

1. **研究効率の向上**
   - クーロンブロッケード現象の特徴を素早く特定
   - データの詳細な分析が容易に
   - 研究時間の短縮

2. **データ理解の促進**
   - 直感的な操作による現象の理解
   - 多角的な視点からのデータ分析
   - 新しい知見の発見支援

3. **研究品質の向上**
   - 正確なデータの可視化と分析
   - 再現性の高い解析
   - 効果的なデータの共有

## 将来の展望

1. **機能拡張**
   - 1次元断面プロットの追加
   - より高度なデータ分析機能
   - バッチ処理機能

2. **ユーザビリティ向上**
   - カスタマイズ可能なショートカットキー
   - プリセット機能
   - 自動解析機能

3. **データ管理**
   - 測定データの管理機能
   - 解析結果の保存と共有
   - レポート生成機能
