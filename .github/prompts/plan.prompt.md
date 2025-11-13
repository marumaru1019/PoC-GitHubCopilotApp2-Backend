---
mode: architect
description: 仕様書から実装計画を作成する
---

# 実装計画ワークフロー

## Context Loading
- 仕様書（`[仕様書フォルダ]/[機能名]/[機能名].spec.md`）を読み込み
- 各リポジトリのディレクトリ構造を確認
- `#codebase` で類似機能を検索

## Execution
責務を分解し（フロントエンド/バックエンド）、変更ファイルをリストアップ。
実装順序と所要時間を見積もる。

## Structured Output
\```markdown
# [機能名] 技術設計書

## バックエンド実装
- [ ] `app/models/[name].py` - [内容]
- [ ] `app/routers/[name].py` - [内容]
- [ ] `tests/test_[name].py` - [内容]

## フロントエンド実装
- [ ] `lib/types.ts` - [内容]
- [ ] `app/[path]/page.tsx` - [内容]
- [ ] `__tests__/[name].test.tsx` - [内容]

## リスク
- [リスク] → [対策]
\```

## Validation Gate
🚨 **STOP**: 実装計画を確認してください。
承認後、`[仕様書フォルダ]/[機能名]/[機能名].plan.md` を作成します。
