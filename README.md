# fin_age_cfd

> **状態: 2025年の個人Windows環境向けCFD実験。現在のままでは再現・運用できません。**

このリポジトリには、TraderMade APIからCFD価格を取得し、加工・可視化するために作成されたPythonコードとNotebookが残っています。汎用的なデータ基盤、継続運用中の収集サービス、再現可能な研究パッケージではありません。

## 現在確認できるもの

- `src/main.py`: TraderMade APIを呼び出して価格データを取得する処理
- `src/config.py`: 取得対象や保存先などの設定
- `bat/set_api_key.bat`: Windowsの環境変数へAPIキーを設定する補助script
- Notebook、生成物、過去のローカル実行環境

## 現在の制約

### 個人環境への固定

`src/config.py`と関連コードは、`D:\_investos\CFD`など特定のWindows絶対pathを前提にしています。別環境でcloneしても、そのままでは動作しません。

### 仮想環境のcommit

`.venv/`配下のsite-packagesがリポジトリに含まれています。これは依存関係の正準ではなく、環境依存・容量・security・license監査上の問題があります。再利用しないでください。

### APIキー設定

`bat/set_api_key.bat`は管理者権限で`setx ... /M`を実行し、APIキーをWindowsのsystem環境変数へ永続設定します。共有PCや通常の開発用途には推奨しません。APIキーをrepository、log、Notebook出力へ保存しないでください。

### 再現性と検証

- 正準な`pyproject.toml`またはlock fileがありません
- CI・自動test・freshness監査を確認できません
- committed dataや生成物の取得日時・source response・hash・再生成手順が整理されていません
- 取得値、計算結果、チャートを現在の市場データとして利用できません

## 現在できないこと

- clone直後の再現可能な実行
- 継続的なCFDデータ収集
- データ鮮度・完全性・API応答の保証
- 本番運用、売買判断、投資助言への利用

## 再開する場合の最低条件

1. `.venv/`と生成済み環境を履歴・配布対象から除外する
2. repository相対pathと明示的な設定fileへ移行する
3. `pyproject.toml`とlock fileで依存を固定する
4. APIキーをprocess単位の環境変数またはsecret managerで扱う
5. raw response、取得日時、symbol、timezone、単位、providerを保存する
6. schema・欠損・重複・freshness testを追加する
7. WindowsとLinuxの再現手順をCIで検証する

## セキュリティ

過去に設定したTraderMade APIキーが現在も有効か確認し、不要または露出の可能性がある場合はprovider側で失効・再発行してください。Gitから文字列を削除するだけでは、漏えい済みcredentialは無効化されません。

## 位置づけ

本リポジトリは、個人環境で行ったCFDデータ処理の過去実験を保存するものです。現行の金融データ基盤として扱わず、再開時は構造・依存・credential・provenanceを作り直してください。

**README監査日:** 2026-08-05
