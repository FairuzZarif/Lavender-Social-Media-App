import base64
import ipaddress
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, NotFound, ParseError

class LavenderAuth(BaseAuthentication):
    api_host = settings.API_HOST
    
    def authenticate(self, request):
        from .models import ShareNodeModel  # Moved imports here to avoid circular import
        from authors.models import AuthorModel
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
    
        try:
            auth_type, credentials = auth_header.split(' ')
            if auth_type.lower() != 'basic':
                return None
            decoded_credentials = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')
        except (ValueError, UnicodeDecodeError):
            raise ParseError()
        
        # Fetch the X-Forwarded-For header for the client's real IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # If multiple proxies exist, we get the first one (the real client IP)
            ip = x_forwarded_for.split(',')[0]
        else:
            # Fallback to REMOTE_ADDR if no X-Forwarded-For header
            ip = request.META.get('REMOTE_ADDR')
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.version == 6:  # IPv6
                ip = f"[{ip}]"
        except:
            pass

        ip = "http://" + ip + "/"
        print(ip)
        x_original_host = request.headers.get('X-Original-Host', ip)
        print(x_original_host)
        if x_original_host == self.api_host:
            try:
                author = AuthorModel.objects.get(username=username)
            except AuthorModel.DoesNotExist:
                raise NotFound()
            if password != author.password:
                raise AuthenticationFailed()
            return (author, None)

        try:
            node = ShareNodeModel.objects.get(host=x_original_host)
            assert node.allowIn
            assert node.inUsername == username
            assert node.inPassword == password
        except:
            raise AuthenticationFailed()
        
        author = AuthorModel.objects.get_or_create(
            username="remoteauth", password="!", id="remoteauth"
        )[0]
        return (author, None)
