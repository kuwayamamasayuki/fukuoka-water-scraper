# 福岡市水道局アプリ - パケットキャプチャ通信解析サマリー

## 概要
このファイルは、福岡市水道局Webアプリケーションの料金データダウンロード機能に関するパケットキャプチャ（decrypted_traffic.pcapng）から抽出した通信データの詳細な解析結果をまとめています。

**解析日時**: 2025年7月24日  
**対象ファイル**: decrypted_traffic.pcapng  
**解析対象**: 料金データダウンロードの完全なワークフロー

---

## 1. 基本情報

### アプリケーション構成
- **フロントエンド**: `https://www.suido-madoguchi-fukuoka.jp`
- **API サーバー**: `https://api.suido-madoguchi-fukuoka.jp`
- **プロトコル**: HTTP/2 over TLS 1.3
- **認証方式**: JWT (JSON Web Token)

### 主要なユーザーID
- **ユーザーID**: `[REDACTED]` (JWTペイロードから抽出)
- **メールアドレス**: `[REDACTED]@example.com`

---

## 2. 認証フロー

### 2.1 ログインリクエスト
```
POST /user/auth/login
Host: api.suido-madoguchi-fukuoka.jp
Content-Type: application/json;charset=utf-8
Content-Length: 81

リクエストボディ:
{
  "loginId": "[REDACTED]@example.com",
  "password": "[REDACTED]"
}
```

### 2.2 JWT トークン情報
```
ヘッダー: {"alg": "RS256", "typ": "JWT"}
ペイロード: {
  "userId": "[REDACTED]",
  "iat": [TIMESTAMP],
  "exp": [TIMESTAMP]
}
有効期限: 1時間 (3600秒)
```

---

## 3. 料金データダウンロードフロー

### 3.1 ファイル作成リクエスト
```
POST /user/file/create/payment/log/[USER_ID]
Host: api.suido-madoguchi-fukuoka.jp
Authorization: [JWT_TOKEN]
Content-Type: application/json;charset=utf-8
Content-Length: 112

リクエストボディ:
{
  "formatType": "2",
  "kenYmFrom": "令和　７年　５月検針分",
  "kenYmTo": "令和　７年　５月検針分"
}
```

**重要なパラメータ:**
- `formatType`: "2" = CSV, "1" = PDF
- `kenYmFrom/kenYmTo`: 和暦形式の期間指定（全角スペース使用）

### 3.2 ダウンロードURL取得リクエスト
```
GET /user/file/download/paylog/[USER_ID]/{filename}
Host: api.suido-madoguchi-fukuoka.jp
Authorization: [JWT_TOKEN]
```

### 3.3 実際のファイルダウンロード
```
GET /paylog/[USER_ID]/{filename}?Expires=...&Signature=...
Host: download.suido-madoguchi-fukuoka.jp
```

---

## 4. HTTPヘッダー詳細解析

### 4.1 CORS プリフライト (OPTIONS) ヘッダー
```
accept: */*
accept-language: ja,en-US;q=0.7,en;q=0.3
accept-encoding: gzip, deflate, br, zstd
priority: u=4
te: trailers
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-site
origin: https://www.suido-madoguchi-fukuoka.jp
referer: https://www.suido-madoguchi-fukuoka.jp/
user-agent: [USER_AGENT_STRING]
```

### 4.2 POST/GET リクエストヘッダー
```
accept: application/json, text/plain, */*
accept-language: ja,en-US;q=0.7,en;q=0.3
accept-encoding: gzip, deflate, br, zstd
priority: u=0
te: trailers
content-type: application/json;charset=utf-8
authorization: [JWT_TOKEN]
origin: https://www.suido-madoguchi-fukuoka.jp
referer: https://www.suido-madoguchi-fukuoka.jp/
user-agent: [USER_AGENT_STRING]
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-site
```

### 4.3 重要な発見
- **ヘッダー名**: 全て小文字（HTTP/2規約準拠）
- **疑似ヘッダー**: `:authority`, `:scheme` は使用されているが、Python requestsライブラリでは処理不可
- **Priority値**: OPTIONS=`u=4`, POST/GET=`u=0`
- **Accept値**: OPTIONS=`*/*`, POST/GET=`application/json, text/plain, */*`

---

## 5. APIレスポンス解析

### 5.1 成功レスポンス
```
ログイン成功:
{
  "result": "00000",
  "token": "[JWT_TOKEN]",
  "userId": "[USER_ID]"
}

ファイル作成成功:
{
  "result": "00000",
  "filename": "riyourireki_[USER_ID]-[TIMESTAMP].csv"
}

ダウンロードURL取得成功:
{
  "result": "00000",
  "downloadUrl": "https://download.suido-madoguchi-fukuoka.jp/paylog/..."
}
```

### 5.2 エラーコード
- **27300**: ファイル作成失敗（認証またはパラメータエラー）
- **21801**: ダウンロードURL取得失敗（認証またはファイル作成エラー）
- **00000**: 成功

---

## 6. データサイズ・形式

### 6.1 実際の料金データ
- **サイズ**: 1KB未満（小さなCSVファイル）
- **形式**: CSV（カンマ区切り）
- **内容**: 実際の料金・使用量データ

### 6.2 設定データ（混同注意）
- **ファイル**: `/assets/message.csv`
- **サイズ**: 128KB
- **内容**: アプリケーション設定・メッセージデータ（料金データではない）

---

## 7. セキュリティ・認証

### 7.1 TLS設定
- **プロトコル**: TLS 1.3
- **セッションID**: `[REDACTED]`
- **セッション有効期限**: 55170秒（約15時間）

### 7.2 CORS設定
- **Origin**: `https://www.suido-madoguchi-fukuoka.jp`
- **Allow-Methods**: POST, GET, OPTIONS
- **Allow-Headers**: authorization, content-type, accept, accept-language, accept-encoding

---

## 8. 実装上の重要なポイント

### 8.1 必須ヘッダー
1. **認証**: `Authorization: {JWT_TOKEN}`
2. **Content-Type**: `application/json;charset=utf-8`
3. **CORS**: `Origin`, `Referer`
4. **ブラウザ識別**: `User-Agent`
5. **Fetch Metadata**: `Sec-Fetch-*`
6. **HTTP/2**: `accept`, `accept-language`, `accept-encoding`, `priority`, `te`

### 8.2 Python requests実装での注意点
- **疑似ヘッダー禁止**: `:authority`, `:scheme` は使用不可
- **ヘッダー名**: 必ず小文字で指定
- **CORS プリフライト**: 手動実装が必要
- **JWT形式**: "Bearer"プレフィックス不要

### 8.3 日付形式
- **API要求形式**: `令和　７年　５月検針分`
- **特徴**: 全角数字、全角スペース使用
- **変換必要**: 西暦→和暦、半角→全角

---

## 9. トラブルシューティング

### 9.1 よくあるエラーと対策
1. **403 Forbidden**: ヘッダー不足・形式不正
2. **27300エラー**: 認証失敗・パラメータ不正
3. **21801エラー**: ファイル作成失敗・認証期限切れ
4. **CORS エラー**: プリフライト失敗・Origin不正

### 9.2 デバッグのポイント
- HTTPリクエスト/レスポンスの完全ログ
- ヘッダー名の大文字小文字確認
- JWT有効期限の確認
- API結果コードの確認

---

## 10. 参考情報

### 10.1 関連ファイル
- `fukuoka_water_downloader_requests.py`: メイン実装
- `test_date_conversion.py`: 日付変換テスト
- `test_workflow.py`: ワークフローテスト
- `debug_output*.log`: デバッグログ

### 10.2 外部リソース
- 福岡市水道局アプリ: https://www.suido-madoguchi-fukuoka.jp/#/login
- HTTP/2仕様: RFC 7540
- CORS仕様: W3C Cross-Origin Resource Sharing

---

**注意**: このドキュメントは実際のパケットキャプチャデータに基づいて作成されており、認証情報やユーザーIDなどの機密情報が含まれています。適切に管理してください。
