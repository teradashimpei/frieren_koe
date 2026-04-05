# 必要な道具を準備する
import streamlit as st
from utils.api import get_posts

# ── タイトルを真ん中に表示する ──
st.markdown("<h1 style='text-align: center;'>Koe&nbsp;を探す 🧐</h1>", unsafe_allow_html=True)

st.markdown("""
<style>
div.stButton > button {
    background-color: #FF6B35;
    color: white;
    border-radius: 8px;
    border: none;
}
div.stButton > button:hover {
    background-color: #E55A25;
    color: white;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ── 画面を3列に分けて真ん中だけ使う（スマホ風にするため）──
col1, col2, col3 = st.columns([1, 2, 1])

with col2:  # 真ん中の列の中に全部書く

    # ── 検索の見出し ──
    st.markdown("### 🔎 キーワード検索")
    
    # キーワードを入力するテキストボックス
    keyword = st.text_input("気になった言葉を入れてください",
                            placeholder="例：ラインB／異音／体調／ベテラン")

    # 「検索する」ボタンが押されたときの処理
    if st.button("検索する", use_container_width=True):
        
        # キーワードが空っぽのときはエラーを出す
        if not keyword:
            st.error("キーワードを入力してください")
        
        else:
            # バックエンドから全件データを取得する
            posts = get_posts()
            
            if posts:
                # キーワードが含まれている投稿だけを絞り込む
                results = [p for p in posts if keyword in str(p)]

                if results:
                    # 何件見つかったか表示する
                    st.success(f"{len(results)}件見つかりました")
                    st.divider()

                    # 1件ずつ表示する
                    for result in results:
                        with st.expander(f"👤 {result.get('author_name', '')}　{result.get('department', '')}"):
                            st.write(result.get("content", ""))
                            if result.get("memo"):
                                st.caption(f"💡 改善点：{result.get('memo', '')}")
                else:
                    # 1件も見つからなかったとき
                    st.warning("該当する事例が見つかりませんでした")
            else:
                # バックエンドがまだ完成していないとき
                st.info("バックエンド接続後に検索できます")