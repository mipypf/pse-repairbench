# リポジトリ構成 v0.1

この文書は、ベンチマークの元データ、派生データ、実行可能インスタンス、
補助スクリプトをリポジトリ内のどこに配置するかを定義する。

## インスタンス

正規のベンチマークインスタンスは `instances/` 配下に配置する。

```text
instances/
  seed/
    <instance_id>/
      instance.json
      public/
      hidden/
  legacy/
    <instance_id>/
      instance.json
      public/
      hidden/
```

`instance.json` は唯一の正規マニフェストファイル名とする。インスタンス
マニフェスト内のパスは、そのマニフェストを含むディレクトリからの相対パス
とする。たとえば seed は、リポジトリ全体からのフルパスを埋め込まずに
`public/problem.md`、`public/streams.csv`、`hidden/base_run.json` を参照
できる。

`public/` には、モデルへ公開または提示してよい成果物だけを置く。問題文、LLM
入力パケット、故障入りフローシート、トポロジー、パラメータ、ストリーム表、
ログなどが該当する。exact gold value を含む決定的なモックモデル出力は
`public/` に置かない。

`hidden/` には、生成と評価にのみ使う成果物を置く。基準フローシート、修復済み
フローシート、基準・故障・修復済みの実行記録、メトリクスレポート、
`hidden/mock_llm_output.json` のような決定的なモック・評価 fixture、その他の
オラクル素材などが該当する。

`instances/seed/` はリリース品質の seed 素材を置く場所である。
`instances/legacy/` は、履歴的な素材やプレースホルダーを可視化しつつ、
リリース準備済みであることを意味しないための場所である。リリースパッケージ
は `instances/seed/*/public/**` のみを抽出して作成する。

## データ系譜

`raw_data/` はダウンロードしたソースアーカイブを保存し、生の入力として扱う。

Historical note: this v0.1 layout kept generated catalogs and screening
summaries in a documentation-side data directory. In the current repository
layout, those tracked metadata files live under `metadata/dwsim_sources/`.

`curated_data/` は、スクリーニングとキュレーションを経て選定されたソース
アーカイブを保存する。これらはまだソース素材であり、ベンチマーク
インスタンスではない。

`instances/` は、キュレーション済み入力から派生した実行可能なベンチマーク
ケースを保存する。ケース単位で public/hidden の分離を強制する最初の場所で
ある。

## スクリプト

スクリプトは運用上の役割ごとに分類する。

- `scripts/validate/`: スキーマ検証とリリースプロファイル検証。
- `scripts/dwsim/`: DWSIM の実行、ワーカー、メトリクス抽出、修復アクション実行。
- `scripts/build_instances/`: 決定的なインスタンスビルダーと legacy seed の準備。
- `scripts/llm/`: LLM 入出力ヘルパーとライブスモークテスト。
- `scripts/maintenance/`: 生データのスクリーニングと curated data の再生成。

maintenance スクリプトは大きな派生データセットを再生成する場合がある。日常的な
検証やスモークテストのコマンドでは、`validate/`、`dwsim/`、`llm/`
サブディレクトリを優先して使う。
