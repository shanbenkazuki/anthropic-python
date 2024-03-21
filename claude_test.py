import anthropic
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()

client = anthropic.Anthropic(
  api_key=os.getenv("ANTHROPIC_API_KEY")
)

message = client.messages.create(
  model="claude-3-haiku-20240307",
  max_tokens=1000,
  temperature=0.0,
  system="Respond only in Yoda-speak.",
  messages=[
    {"role": "user", "content": "How are you today?"}
  ]
)

print(message.content)