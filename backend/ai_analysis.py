import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from typing import Literal
from pydantic import BaseModel

class ReportAnalysis(BaseModel):
    case_summary: str
    issue_type: Literal[
        "通常業務",
        "進捗遅れ",
        "トラブル対応",
        "品質",
        "設備・システム",
        "連携・確認",
        "改善提案",
        "気づき・学び",
        "安全",
        "その他",
    ]
    should_save: bool

load_dotenv()
# st.secretsにキーがあればそれを使い、なければos.getenv(.env)を使う
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key)


def build_analysis_input(data: dict) -> str:
    return f"""
日報内容:
{data.get("content") or ""}

気づき・改善案:
{data.get("improvement") or ""}

補足:
{data.get("notes") or ""}

作業は円滑だったか:
{data.get("is_smooth")}

緊急度:
{data.get("urgency") or ""}
""".strip()


def analyze_report_with_openai(data: dict) -> dict:
    analysis_input = build_analysis_input(data)

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": """
あなたは日報を整理して検索しやすくする担当者です。
与えられた日報から、次の3項目を作成してください。

項目:
- case_summary
- issue_type
- should_save

ルール:
- case_summary:
  - 50文字以内
  - 日報内容だけでなく、気づきや改善案、補足も見て要約する
  - 事実ベースで簡潔に書く
  - 箇条書きにしない
  - 推測しない

- issue_type:
  - 次の候補から1つだけ選ぶ
  - 通常業務
  - 進捗遅れ
  - トラブル対応
  - 品質
  - 設備・システム
  - 連携・確認
  - 改善提案
  - 気づき・学び
  - 安全
  - その他

- should_save:
  - 次の場合は false
    - 通常業務である
    - 大きな問題やトラブルがない
    - 気づきや改善案として残す価値も低い
    - 後で検索対象にする必要性が低い
  - 次の場合は true
    - 問題、遅れ、ミス、確認待ち、トラブルがある
    - 改善案や気づきがある
    - 後で似た事例として検索したい内容である
    - 通常業務でも、共有価値や再利用価値がある

判断の考え方:
- 改善の提案が主なら「改善提案」
- 学びや発見が主なら「気づき・学び」
- 機械、端末、アプリ、通信などの不具合は「設備・システム」
- やり直し、不良、誤りは「品質」
- 遅れや未完了は「進捗遅れ」
- 調整、確認待ち、引継ぎは「連携・確認」
- 特に問題なく、記録として残す価値が薄ければ「通常業務」かつ should_save=false
""".strip(),
            },
            {
                "role": "user",
                "content": analysis_input,
            },
        ],
        text_format=ReportAnalysis,
    )

    parsed = response.output_parsed

    return {
        "case_summary": parsed.case_summary,
        "issue_type": parsed.issue_type,
        "should_save": parsed.should_save,
    }