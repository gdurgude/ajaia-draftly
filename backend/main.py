"""Docspace: focused document editor API. Demo identities are not authentication."""
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from html import escape
from typing import Literal

import bleach
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime, UniqueConstraint, select, or_
from sqlalchemy.orm import declarative_base, sessionmaker, Session

ROOT = Path(__file__).resolve().parent.parent
DB_URL = os.getenv('DATABASE_URL', f'sqlite:///{ROOT / "docspace.db"}')
if DB_URL.startswith('postgres://'):
    DB_URL = DB_URL.replace('postgres://', 'postgresql+psycopg://', 1)
if DB_URL.startswith('postgresql://'):
    DB_URL = DB_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
engine = create_engine(DB_URL, connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite:') else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(160), nullable=False, unique=True)

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(120), nullable=False)
    html = Column(Text, nullable=False, default='<p></p>')
    updated_at = Column(DateTime(timezone=True), nullable=False)

class Share(Base):
    __tablename__ = 'shares'
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    __table_args__ = (UniqueConstraint('document_id', 'user_id'),)

Base.metadata.create_all(engine)
with SessionLocal() as db:
    for id_, name, email in [(1, 'Alex Morgan', 'alex@demo.local'), (2, 'Jordan Lee', 'jordan@demo.local')]:
        if not db.get(User, id_):
            db.add(User(id=id_, name=name, email=email))
    db.commit()

app = FastAPI(title='Docspace API')
TAGS = ['p','br','b','strong','i','em','u','h1','h2','h3','ul','ol','li','blockquote','div']

def clean(html: str) -> str:
    # No attributes, scripts, links, images, or pasted inline styles.
    return bleach.clean(html, tags=TAGS, attributes={}, strip=True)

def db_session():
    with SessionLocal() as db:
        yield db

def actor(x_user_id: int = Header(default=1), db: Session = Depends(db_session)) -> User:
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(401, 'Unknown demo user')
    return user

def readable(db, doc_id, user):
    doc = db.get(Document, doc_id)
    if doc is None or (doc.owner_id != user.id and not db.scalar(select(Share.id).where(Share.document_id == doc_id, Share.user_id == user.id))):
        raise HTTPException(404, 'Document not found or not shared with you')
    return doc

def owned(db, doc_id, user):
    doc = readable(db, doc_id, user)
    if doc.owner_id != user.id:
        raise HTTPException(403, 'Only the owner can make changes')
    return doc

def doc_json(db, doc, user):
    owner = db.get(User, doc.owner_id)
    shares = db.scalars(select(Share).where(Share.document_id == doc.id)).all()
    return {'id': doc.id, 'title': doc.title, 'html': doc.html,
            'owner_id': owner.id, 'owner': owner.name, 'is_owner': owner.id == user.id,
            'shared_with': [{'id': s.user_id, 'name': db.get(User, s.user_id).name} for s in shares],
            'updated_at': doc.updated_at.isoformat()}

class DocIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    html: str = Field(default='<p></p>', max_length=200_000)

class DocPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    html: str | None = Field(default=None, max_length=200_000)

class ShareIn(BaseModel):
    user_id: int

@app.get('/api/users')
def users(db: Session = Depends(db_session)):
    return [{'id': u.id, 'name': u.name} for u in db.scalars(select(User).order_by(User.id))]

@app.get('/api/documents')
def list_documents(user: User = Depends(actor), db: Session = Depends(db_session)):
    shared_ids = select(Share.document_id).where(Share.user_id == user.id)
    docs = db.scalars(select(Document).where(or_(Document.owner_id == user.id, Document.id.in_(shared_ids))).order_by(Document.updated_at.desc())).all()
    return [doc_json(db, d, user) for d in docs]

@app.post('/api/documents', status_code=201)
def create_document(body: DocIn, user: User = Depends(actor), db: Session = Depends(db_session)):
    title = body.title.strip()
    if not title:
        raise HTTPException(422, 'Title cannot be blank')
    doc = Document(title=title, html=clean(body.html), owner_id=user.id, updated_at=datetime.now(timezone.utc))
    db.add(doc); db.commit(); db.refresh(doc)
    return doc_json(db, doc, user)

@app.get('/api/documents/{doc_id}')
def get_document(doc_id: int, user: User = Depends(actor), db: Session = Depends(db_session)):
    return doc_json(db, readable(db, doc_id, user), user)

@app.patch('/api/documents/{doc_id}')
def update_document(doc_id: int, body: DocPatch, user: User = Depends(actor), db: Session = Depends(db_session)):
    doc = owned(db, doc_id, user)
    if body.title is not None:
        if not body.title.strip():
            raise HTTPException(422, 'Title cannot be blank')
        doc.title = body.title.strip()
    if body.html is not None:
        doc.html = clean(body.html)
    doc.updated_at = datetime.now(timezone.utc)
    db.commit()
    return doc_json(db, doc, user)

@app.post('/api/documents/{doc_id}/share')
def share_document(doc_id: int, body: ShareIn, user: User = Depends(actor), db: Session = Depends(db_session)):
    doc = owned(db, doc_id, user)
    if body.user_id == user.id:
        raise HTTPException(400, 'Owner already has access')
    if not db.get(User, body.user_id):
        raise HTTPException(404, 'User not found')
    exists = db.scalar(select(Share.id).where(Share.document_id == doc.id, Share.user_id == body.user_id))
    if not exists:
        db.add(Share(document_id=doc.id, user_id=body.user_id)); db.commit()
    return doc_json(db, doc, user)

@app.delete('/api/documents/{doc_id}/share/{recipient_id}')
def unshare_document(doc_id: int, recipient_id: int, user: User = Depends(actor), db: Session = Depends(db_session)):
    doc = owned(db, doc_id, user)
    share = db.scalar(select(Share).where(Share.document_id == doc_id, Share.user_id == recipient_id))
    if not share:
        raise HTTPException(404, 'Share not found')
    db.delete(share); db.commit()
    return doc_json(db, doc, user)

@app.post('/api/import', status_code=201)
async def import_file(file: UploadFile = File(...), user: User = Depends(actor), db: Session = Depends(db_session)):
    filename = Path(file.filename or '').name
    if Path(filename).suffix.lower() not in ('.txt', '.md'):
        raise HTTPException(415, 'Only .txt and .md files are supported')
    raw = await file.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise HTTPException(413, 'Maximum file size is 1 MB')
    try:
        content = raw.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(422, 'File must be UTF-8 encoded')
    # Explicitly import markdown as plain text, preserving line breaks but not markdown syntax.
    html = '<p>' + escape(content).replace('\n', '<br>') + '</p>'
    title = (Path(filename).stem or 'Imported document')[:120]
    doc = Document(title=title, html=clean(html), owner_id=user.id, updated_at=datetime.now(timezone.utc))
    db.add(doc); db.commit(); db.refresh(doc)
    return doc_json(db, doc, user)

STATIC = ROOT / 'frontend'
@app.get('/')
def index():
    return FileResponse(STATIC / 'index.html')
app.mount('/static', StaticFiles(directory=STATIC), name='static')
