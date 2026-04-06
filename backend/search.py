
def search_fulltext(query: str, analysis_reports: list) -> list:
    """
    全文検索（本文含む）を実行し、マッチ数でスコアリングする。

    Args:
        query: 検索キーワード
        analysis_reports: ページリスト

    Returns:
        マッチしたページのリスト（スコア降順）
    """
    if not query.strip():
        return []

    results = []
    q = query.lower()

    for analysis_report in analysis_reports:
        text = " ".join([
            analysis_report.get("case_summary", ""),
            analysis_report.get("issue_type", ""),
        ]).lower()

        count = text.count(q)
        if count > 0:
            r = analysis_report.copy()
            r["match_count"] = count
            r["preview"] = _make_preview(analysis_report.get("case_summary", analysis_report.get("issue_type", "")), query)
            results.append(r)

    results.sort(key=lambda x: x["issue_type"], reverse=True)
    return results

def _make_preview(text: str, query: str, ctx: int = 80) -> str:
    """マッチ箇所周辺のプレビューを生成する。"""
    if not text or not query:
        return ""

    pos = text.lower().find(query.lower())
    if pos == -1:
        return (text[:200] + "...") if len(text) > 200 else text

    start = max(0, pos - ctx)
    end = min(len(text), pos + len(query) + ctx)

    preview = ""
    if start > 0:
        preview += "..."
    preview += text[start:end]
    if end < len(text):
        preview += "..."
    return preview
