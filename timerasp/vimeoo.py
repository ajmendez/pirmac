'''
vimeoo is for vimeo without collision
'''
import vimeo
from pymendez import auth



def upload(filename):
    ident, secret, token = auth('vimeo', ['client_id', 'client_secret', 'token'])
    api = vimeo.VimeoClient(token=token, key=ident, secret=secret)
    
    print 'Uploading...'
    api.upload(filename)
    print 'Done!'