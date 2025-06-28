import requests
import json
# os.environ['OPENROUTER_API_KEY'] = "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-YQ"

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": 'Bearer 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',
    "Content-Type": "application/json",
    # "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    # "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "mistralai/mistral-small-3.2-24b-instruct:free",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What is ai"
          },
        #   {
        #     "type": "image_url",
        #     "image_url": {
        #       "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
        #     }
        #   }
        ]
      }
    ],
    
  })
)
print(response.json())