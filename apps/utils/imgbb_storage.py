"""ImgBB storage backend for Django."""
import base64
import requests
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile


class ImgBBStorage(Storage):
    """Custom storage backend for ImgBB."""
    
    def __init__(self):
        self.api_key = settings.IMGBB_API_KEY
        self.api_url = settings.IMGBB_API_URL
    
    def _save(self, name, content):
        """Upload file to ImgBB and return URL."""
        try:
            # Read file content
            file_content = content.read()
            
            # Encode to base64
            encoded_image = base64.b64encode(file_content).decode('utf-8')
            
            # Upload to ImgBB
            payload = {
                'key': self.api_key,
                'image': encoded_image,
                'name': name
            }
            
            response = requests.post(self.api_url, data=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                # Return the full URL
                return result['data']['url']
            else:
                raise Exception(f"ImgBB upload failed: {result}")
                
        except Exception as e:
            raise Exception(f"Failed to upload to ImgBB: {str(e)}")
    
    def _open(self, name, mode='rb'):
        """Open file from ImgBB (download)."""
        try:
            response = requests.get(name, timeout=30)
            response.raise_for_status()
            return ContentFile(response.content)
        except Exception as e:
            raise Exception(f"Failed to open file from ImgBB: {str(e)}")
    
    def delete(self, name):
        """ImgBB free plan doesn't support deletion via API."""
        pass
    
    def exists(self, name):
        """Check if file exists (always return False to force upload)."""
        return False
    
    def url(self, name):
        """Return the URL - ImgBB returns full URL."""
        return name
    
    def size(self, name):
        """Get file size."""
        try:
            response = requests.head(name, timeout=10)
            return int(response.headers.get('Content-Length', 0))
        except:
            return 0
