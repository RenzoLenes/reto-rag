import base64
from openai import OpenAI
from typing import List, Dict, Any
from core.config import settings


class ImageSummarizer:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"
    
    def caption_image(self, image_data: bytes) -> str:
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image briefly and factually in 2-4 lines. Focus on the main visual elements, objects, text, charts, diagrams, or any important content that would be useful for document search and retrieval."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error captioning image: {e}")
            return "Image could not be processed for description."
    
    def caption_multiple_images(self, images_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        captioned_images = []
        
        for image_info in images_data:
            caption = self.caption_image(image_info["image_data"])
            
            captioned_image = {
                "page": image_info["page"],
                "image_index": image_info["image_index"],
                "caption": caption,
                "source": image_info["source"]
            }
            
            captioned_images.append(captioned_image)
        
        return captioned_images


image_summarizer = ImageSummarizer()