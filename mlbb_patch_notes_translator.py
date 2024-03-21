import json
import anthropic
from dotenv import load_dotenv
import os
from typing import List

# .envファイルから環境変数を読み込む
load_dotenv()

# Anthropic APIクライアントを作成
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# mlbb_hero.jsonファイルを読み込む
with open("mlbb_hero.json", "r") as file:
    hero_data = json.load(file)

# 英語の固有名詞と日本語訳の辞書型を作成
translations = {hero["name_en"]: hero["name_jp"] for hero in hero_data}

# mlbb-1.8.66-patch-notes.txtファイルを読み込む
with open("patch-notes/mlbb-1.8.66.txt", "r") as file:
    patch_notes = file.read()

def split_text(text: str, max_tokens: int) -> List[str]:
    """
    テキストを指定された最大トークン数に基づいて分割する関数。
    
    Args:
        text (str): 分割するテキスト。
        max_tokens (int): 各チャンクの最大トークン数。
    
    Returns:
        List[str]: 分割されたテキストのチャンクのリスト。
    """
    # テキストを単語に分割
    words = text.split()
    chunks = []
    current_chunk = []

    # 単語を最大トークン数に収まるようにチャンクに分割
    for word in words:
        if len(" ".join(current_chunk + [word])) <= max_tokens:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    # 最後のチャンクを追加
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def translate_text(text: str) -> str:
    """
    テキストを翻訳する関数。
    
    Args:
        text (str): 翻訳するテキスト。
    
    Returns:
        str: 翻訳されたテキスト。
    """
    # Anthropic APIを使用してテキストを翻訳
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0.7,
        system="""
<response>
<instruction>あなたは海外ゲームの英語版アップデートの日本語翻訳をサポートするアシスタントです。</instruction>
<steps>
<step>自然でわかりやすい日本語で翻訳してください。</step>
<step>ゲーム関連用語や固有名詞は、適切な日本語訳や原語を使用してください。</step>
<step>文脈に応じて、丁寧語や敬語を適切に使用する。</step>
<step>原文の意味や語調をできるだけ崩さないように翻訳する。</step>
<step>必要に応じて、ヘッダー、リスト、その他のフォーマット要素を含め、Markdown構文を使用して翻訳結果をフォーマットしてください。</step>
<step>翻訳対象のテキストに含まれる固有名詞は、提供される辞書を使用して日本語に置き換えてから翻訳を行ってください。</step>
</steps>
<note>翻訳されるテキストと固有名詞の辞書は次のメッセージで提供されます。翻訳されたテキストのみをMarkdownでフォーマットして日本語で返信してください。</note>
</response>
""",
        messages=[
            {"role": "user", "content": f"Patch Notes:\n{text}\n\nTranslations:\n{json.dumps(translations)}"}
        ]
    )
    # 翻訳されたテキストを抽出
    translated_text = "".join([content_block.text for content_block in message.content if content_block.type == "text"])
    
    # 翻訳されたテキストの "[" と "]" を "【" と "】" に置き換える
    translated_text = translated_text.replace("[", "【").replace("]", "】")
    
    return translated_text

# テキストを4096トークンずつに分割
text_chunks = split_text(patch_notes, max_tokens=4096)

# 分割されたテキストを翻訳し、結合
translated_text = "".join([translate_text(chunk) for chunk in text_chunks])

# 翻訳結果をMarkdownファイルとして保存
with open("translated_patch_notes.md", "w") as output_file:
    output_file.write(translated_text)