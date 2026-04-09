from django.shortcuts import render
from .models import Message

def index(request):
    # Get last 50 messages for history
    messages = Message.objects.all().order_by('timestamp')[:50]
    return render(request, 'chat/index.html', {'messages': messages})
