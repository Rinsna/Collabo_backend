# -*- coding: utf-8 -*-
"""
Test script to verify emoji encoding support across the application.
Run this to ensure emojis display correctly.
"""

import sys
import json

def test_emoji_encoding():
    """Test various emoji encodings"""
    
    print("=" * 60)
    print("EMOJI ENCODING TEST")
    print("=" * 60)
    print()
    
    # Test basic emojis
    emojis = {
        'faces': '😀 😃 😄 😁 😆 😅 🤣 😂',
        'hearts': '❤️ 💕 💖 💗 💓 💞 💝',
        'symbols': '✨ ⭐ 🌟 💫 ⚡ 🔥 💥',
        'objects': '📱 💻 📷 🎥 🎬 🎨 🎭',
        'activities': '⚽ 🏀 🏈 ⚾ 🎾 🏐 🏉',
        'food': '🍕 🍔 🍟 🌭 🍿 🧂 🥤',
        'travel': '✈️ 🚗 🚕 🚙 🚌 🚎 🏎️',
        'flags': '🇮🇳 🇺🇸 🇬🇧 🇨🇦 🇦🇺 🇯🇵'
    }
    
    print("Testing emoji categories:")
    print()
    
    for category, emoji_string in emojis.items():
        print(f"{category.capitalize()}: {emoji_string}")
    
    print()
    print("=" * 60)
    print("JSON ENCODING TEST")
    print("=" * 60)
    print()
    
    # Test JSON encoding
    test_data = {
        'username': 'test_user',
        'bio': 'I love coding! 💻 ✨',
        'category': 'Tech 💻',
        'location': 'Mumbai 🇮🇳',
        'interests': ['Fashion 👗', 'Beauty 💄', 'Travel ✈️']
    }
    
    json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
    print("JSON with emojis:")
    print(json_str)
    
    print()
    print("=" * 60)
    print("SYSTEM ENCODING INFO")
    print("=" * 60)
    print()
    
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"Filesystem encoding: {sys.getfilesystemencoding()}")
    print(f"stdout encoding: {sys.stdout.encoding}")
    
    print()
    print("=" * 60)
    print("TEST COMPLETE ✅")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        test_emoji_encoding()
        print("\n✅ All emoji encoding tests passed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
