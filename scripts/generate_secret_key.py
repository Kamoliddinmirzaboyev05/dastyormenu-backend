#!/usr/bin/env python3
"""
Django SECRET_KEY generator
Usage: python scripts/generate_secret_key.py
"""
import secrets
import string

def generate_secret_key(length=50):
    """Generate a random SECRET_KEY for Django."""
    chars = string.ascii_letters + string.digits + string.punctuation
    # Remove quotes to avoid issues
    chars = chars.replace("'", "").replace('"', "").replace('\\', '')
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == '__main__':
    key = generate_secret_key()
    print("\n" + "="*60)
    print("Django SECRET_KEY Generated!")
    print("="*60)
    print(f"\nSECRET_KEY={key}")
    print("\n" + "="*60)
    print("Copy the line above and paste it in Railway environment variables")
    print("="*60 + "\n")
