
todo: 適当にAI に書かせているので後で整備



# tool.py

Native Instruments 製品のレジストリに登録されている `ContentDir` を走査し、
指定したパスに一致するものだけを条件付きで書き換える CLI ツールです。

主に **ライブラリ配置の整理・移行** を目的としています。

---

## 何をするツールか

* `HKEY_LOCAL_MACHINE\SOFTWARE\Native Instruments` 配下のサブキーを列挙
* `ContentDir` を持つエントリのみを対象にする
* `ContentDir` を一時的に正規化して比較

  * 末尾のバックスラッシュを除去
* 指定されたパス集合に **完全一致** した場合のみ書き換え
* 新しい `ContentDir` は以下の形式になる

```
<元のパス> Library\
```

---

## 動作例（概念）

| 元の ContentDir | 指定パス    | 判定  | 新しい ContentDir   |
| ------------- | ------- | --- | ---------------- |
| `D:\NI\`      | `D:\NI` | 一致  | `D:\NI Library\` |
| `C:\Samples\` | `D:\NI` | 不一致 | 変更なし             |

---

## 要件

* Windows
* Python 3.9 以降（目安）
* 管理者権限

  * `HKEY_LOCAL_MACHINE` を書き換えるため必須

※ 標準ライブラリのみ使用しています（外部依存なし）

---

## インストール

特別なインストールは不要です。
スクリプトをそのまま配置してください。

```bash
git clone <this-repository>
cd <this-repository>
```

---

## 使い方

```
script_name.py [--dry-run] <paths>...
```

### 引数

#### `paths`（必須）

* 1つ以上指定可能
* 比較対象となるベースパス
* 内部では set に格納され、末尾の `\` は無視されます

例：

```bash
python script.py D:\NI C:\Samples
```

#### `--dry-run`（任意）

* 実際には書き換えを行わず
* 対象となるアイテムと変更内容のみを表示します

---

## 実行例

### dry-run（確認のみ）

```bash
python script.py --dry-run D:\NI
```

出力例：

```
[DRY-RUN] Kontakt ContentDir: 'D:\NI\' -> 'D:\NI Library\'
```

### 実際に書き換える場合

```bash
python script.py D:\NI
```

出力例：

```
[WRITE] Kontakt ContentDir: 'D:\NI\' -> 'D:\NI Library\'
```

---

## 安全設計について

* レジストリ値は **直接比較しません**

  * 比較用に一時的に正規化した値のみを使用
* `--dry-run` を指定しない限り、表示と書き込みは明確に分離されています
* 条件に一致しないエントリは一切変更されません

---

## 注意事項

* 本ツールは **ContentDir のみ** を対象とします
* 他のレジストリ値（InstallDir 等）には影響しません
* 実行前に必ず `--dry-run` で確認することを推奨します

---

## ライセンス

必要に応じて追記してください。


# migrate_ni_contents.py

Native Instruments のコンテンツディレクトリ
`NI_Contents` 配下に混在する

* `名前`
* `名前 Library`

といった **重複・揺らぎのあるディレクトリ構成**を整理するための CLI ツールです。

破壊的操作はすべて `--dry-run` に対応しており、
**実行前に必ず結果を確認できる設計**になっています。

---

## 機能概要

本ツールは以下の 2 つのサブコマンドを提供します。

* `move`
  `* Library` ディレクトリをバックアップ領域へ移動
* `rename`
  指定したディレクトリ名の末尾に `" Library"` を付与

---

## 前提ディレクトリ構成

```text
C:\mnt2\#Composing\libraries\
├─ NI_Contents
│  ├─ Foo
│  ├─ Foo Library
│  ├─ Bar
│  └─ Baz Library
└─ NI_Contents.bak   (move コマンドで使用)
```

---

## インストール / 実行

特別な依存はありません。
Python 3.10 以降を推奨します。

```bash
python tool.py --help
```

---

## move コマンド

### 概要

`NI_Contents` 直下にある
**末尾が `" Library"` のディレクトリ**を

```
C:\mnt2\#Composing\libraries\NI_Contents.bak
```

へ移動します。

---

### dry-run（強く推奨）

```bash
python tool.py move --dry-run
```

出力例:

```text
[DRY-RUN] move: C:\...\NI_Contents\Foo Library
[DRY-RUN] move: C:\...\NI_Contents\Baz Library
```

---

### 実行

```bash
python tool.py move
```

出力例:

```text
move: C:\...\NI_Contents\Foo Library -> C:\...\NI_Contents.bak\Foo Library
```

---

## rename コマンド

### 概要

引数で指定した **1つ以上のディレクトリ**に対して、

* 末尾に `" Library"` を付与
* すでに付いている場合はスキップ

を行います。

---

### dry-run

```bash
python tool.py rename --dry-run "C:\path\to\Foo"
```

出力例:

```text
[DRY-RUN] rename: C:\path\to\Foo -> C:\path\to\Foo Library
```

---

### 実行

```bash
python tool.py rename "C:\path\to\Foo" "C:\path\to\Bar"
```

出力例:

```text
rename: C:\path\to\Foo -> C:\path\to\Foo Library
rename: C:\path\to\Bar -> C:\path\to\Bar Library
```

---

## 安全設計について

* すべての破壊的操作に `--dry-run` を用意
* ディレクトリでないパスは自動的にスキップ
* すでに期待状態のものは変更しない
* 名前ルールは `" Library"` に一本化

「何が起きるかわからない操作」を
**必ず事前に目で確認できる**ことを最優先しています。

---

## 将来の拡張余地

* 重複ペア（`名前` / `名前 Library`）を検出して制御
* 孤立した Library のみ move
* 実行計画を JSON で出力
* 対話確認 (`--yes`) の追加

設計はこれらの拡張を前提にしています。

---

## 注意

* 実行前に **必ず `--dry-run` を確認してください**
* バックアップ先は自動作成されますが、中身の衝突には注意してください
* 大量操作前には手動バックアップを推奨します
