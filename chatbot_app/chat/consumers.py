import json
import asyncio
import httpx
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from django.conf import settings
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        user_message = text_data_json['message']

        # Save user message to history
        await sync_to_async(Message.objects.create)(
            role='user',
            content=user_message
        )

        # Prepare messages for Ollama (including history)
        history = await sync_to_async(list)(
            Message.objects.all().order_by('timestamp')[:20]
        )
        messages = [
            {'role': m.role, 'content': m.content} for m in history
        ]

        # Send empty assistant message to UI to prepare for stream
        await self.send(text_data=json.dumps({
            'type': 'start',
            'role': 'assistant'
        }))

        full_response = ""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST", 
                    f"{settings.OLLAMA_HOST}/api/chat",
                    json={
                        "model": "mistral",
                        "messages": messages,
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            chunk = json.loads(line)
                            if 'message' in chunk:
                                content = chunk['message'].get('content', '')
                                full_response += content
                                await self.send(text_data=json.dumps({
                                    'type': 'chunk',
                                    'content': content
                                }))
                            if chunk.get('done'):
                                break
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'content': str(e)
            }))

        # Save assistant response to history
        if full_response:
            await sync_to_async(Message.objects.create)(
                role='assistant',
                content=full_response
            )

        # Notify UI stream is done
        await self.send(text_data=json.dumps({
            'type': 'done'
        }))
