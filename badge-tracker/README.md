# badge-tracker

GMOコマース バッジ取得状況トラッカー  
CSVをアップするだけでNetlifyサイトが自動更新される仕組みです。

## リポジトリ構成

```
badge-tracker/
├── gmo_badges.csv          ← ★ここを更新するだけ！
├── badges.json             ← バッジ画像データ（base64）
├── index.html              ← 自動生成（Gitで管理しない）
├── scripts/
│   └── generate_html.py   ← CSV+JSON → index.html 生成スクリプト
└── .github/
    └── workflows/
        └── deploy.yml      ← GitHub Actions 設定
```

## 週次更新手順（これだけ！）

1. nasa.gmo.jp でブックマークレット実行 → `gmo_badges.csv` ダウンロード
2. このリポジトリの `gmo_badges.csv` をそのファイルで上書き
3. GitHubにプッシュ（またはGitHub上でファイルを直接アップロード）
4. **自動で** GitHub Actions → HTML生成 → Netlify公開 が走る！

## GitHub Secrets の設定（初回のみ）

リポジトリの Settings → Secrets and variables → Actions で以下を登録：

| Name | Value |
|------|-------|
| `NETLIFY_SITE_ID` | `2ddbe70d-7d1c-4e64-8a1c-e37b4aa1ff38` |
| `NETLIFY_AUTH_TOKEN` | NetlifyのAPIトークン |

## CSVフォーマット

```
部署,氏名,読み,社員番号,バッジ一覧(|区切り)
オペレーション本部 > ...,山田 太郎（ﾔﾏﾀﾞ ﾀﾛｳ）,,,虎の穴｜ベーシック|虎の穴｜アドバンス
```

## 公開URL

https://stellular-ganache-a01abc.netlify.app
