from openai import OpenAI

class LLMClient:
    def __init__(self, api_key, api_url="https://api.deepseek.com", model="deepseek-chat"):
        self.client = OpenAI(api_key=api_key, base_url=api_url)
        self.model = model

    def send_request(self, content, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content},
                ],
                stream=False
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": self.model,
                "usage": response.usage.dict() if response.usage else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }