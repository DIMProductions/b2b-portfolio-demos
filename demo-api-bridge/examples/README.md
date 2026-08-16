# サンプル事例

## 正常系: 旧形式ペイロード → 新形式API

Bridgeへのリクエスト(`POST /bridge/sync`、ヘッダー`Idempotency-Key: <uuid>`):

```json
{
  "customer_id": "001",
  "full_name": "Taro Yamada",
  "tel": "090-1234-5678",
  "api_key": "secret-key-123"
}
```

`input/mapping_rules.json`が変換を制御します(`customer_id → id`、`full_name → name.full`、`tel → phone`)。Bridgeはこれをupstreamへ転送する前に変換します:

```json
{
  "id": "001",
  "name": {
    "full": "Taro Yamada"
  },
  "phone": "090-1234-5678"
}
```

`api_key`はマッピングの時点で意図的に除外され(upstreamには一切転送されない)、全てのログ行でマスキング(`***`)されます — `output/example_logs.jsonl`参照。

## エラー系: upstreamがリトライの末に成功する

`src/mock_upstream.py`は、最初の2回は`503`を返し3回目に`200`を返す不安定なupstreamをシミュレートします。Bridgeの`tenacity`ベースのリトライ(指数バックオフ、最大3回)がこれを透過的に吸収するため、呼び出し側には最終的な`200`しか見えません。これは実際に検証済みです: 実際に動作中のmock-upstreamプロセスに対してリクエストを送ったところ、`503`が2回ログに記録された後に`200`が1回記録され、これがすべて呼び出し元から見た1回のリクエスト内で完結していることを確認しました。2つの最終的な結果(リトライ枯渇 vs 成功)については`output/success_response.json` / `output/upstream_error.json`を参照してください。

## 冪等性系: 同一キーでupstreamへの重複呼び出しなし

同一の`Idempotency-Key`で同じリクエストを2回送ると、2回目はRedisにヒットしてキャッシュされたレスポンスが返されます。mock-upstreamプロセス側の不安定挙動用カウンターは2回目の呼び出しで進まないため、upstreamが実際には再呼び出しされていないことが確認できます。
