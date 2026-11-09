import os
import tempfile
from pathlib import Path

test_db = Path(tempfile.gettempdir()) / "ajaia_test_docspace.db"

os.environ["DATABASE_URL"] = f"sqlite:///{test_db.as_posix()}"

try:
    test_db.unlink()
except FileNotFoundError:
    pass
from fastapi.testclient import TestClient
from backend.main import app

client=TestClient(app)
def who(i): return {'X-User-Id':str(i)}

def test_create_save_share_permissions_and_sanitization():
    d=client.post('/api/documents',headers=who(1),json={'title':'Planning','html':'<p><strong>Hello</strong><script>alert(1)</script></p>'})
    assert d.status_code==201
    id_=d.json()['id']
    assert '<script>' not in d.json()['html']
    assert '<strong>Hello</strong>' in d.json()['html']
    assert client.get(f'/api/documents/{id_}',headers=who(2)).status_code==404
    assert client.post(f'/api/documents/{id_}/share',headers=who(1),json={'user_id':2}).status_code==200
    shared=client.get('/api/documents',headers=who(2)).json()
    assert any(item['id']==id_ and not item['is_owner'] for item in shared)
    assert client.patch(f'/api/documents/{id_}',headers=who(2),json={'title':'Oops'}).status_code==403
    assert client.patch(f'/api/documents/{id_}',headers=who(1),json={'html':'<h2>Saved</h2>'}).status_code==200
    assert client.get(f'/api/documents/{id_}',headers=who(1)).json()['html']=='<h2>Saved</h2>'
    assert client.delete(f'/api/documents/{id_}/share/2',headers=who(1)).status_code==200
    assert client.get(f'/api/documents/{id_}',headers=who(2)).status_code==404

def test_upload_validation():
    invalid=client.post('/api/import',headers=who(1),files={'file':('bad.html',b'<script>x</script>','text/html')})
    assert invalid.status_code==415
    valid=client.post('/api/import',headers=who(1),files={'file':('notes.txt',b'hello\nworld','text/plain')})
    assert valid.status_code==201
    assert 'hello<br>world' in valid.json()['html']
