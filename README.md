# DIMProductions — 成果物単位の請負デモ集

BPパートナー募集企業様向けのポートフォリオです。SESでの人員提供ではなく、**「仕様書 / サンプルデータを渡すと、決められた形式の成果物が返ってくる」**請負のかたちを、実際に動くコードで示しています。

3つのデモはすべて同じ構成・同じ起動方法です。

```
demo-xxx/
├── README.md          # Input → Processing → Output のフロー図と使い方
├── docker-compose.yml # 一発起動用
├── input/              # 渡されるデータのモック
├── src/                 # 実装コード
├── tests/               # 自動テスト
├── output/              # 処理結果
└── examples/            # 正常系・異常系の具体例
```

## デモ一覧

### [demo-structured-data-pipeline](demo-structured-data-pipeline/) — データ処理代行
PDF帳票 + Excel一括データ → 正規化・重複排除・JSON Schema検証 → `output.json` / `errors.csv` / `validation_report.json`。
生成AIらしい「あいまいな補完」はせず、スキーマに合わないデータは即エラーとして分離します。同じ入力からは常に同じ出力(bit単位で再現可能)。

### [demo-regression-pack](demo-regression-pack/) — テスト自動化(システム評価)
`test_spec.yaml`(人間が書くテスト仕様)を渡すだけで、Playwrightによるログイン・検索・フォーム送信・APIレスポンス確認までを自動実行。`junit.xml` / HTMLレポート / 失敗時スクリーンショット・トレースをGitHub Actions上でも生成します。

### [demo-api-bridge](demo-api-bridge/) — API連携(モジュール請負)
旧形式APIのリクエストを、フィールドマッピング・リトライ・タイムアウト・冪等性・構造化ログを備えたBridge経由で新形式APIに変換。単なる中継ではなく、本番投入を想定した堅牢性を実装しています。

## 実行方法
各ディレクトリで:
```bash
docker-compose up --build
```
だけで完結します(個別の手順は各`README.md`を参照)。
