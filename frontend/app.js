const $ = (s) => document.querySelector(s);
let userId = 1, docs = [], current = null, saveTimer = null, requestToken = 0;
const API = '/api';
function toast(message){ const el=$('#toast');el.textContent=message;el.style.display='block';clearTimeout(el.timer);el.timer=setTimeout(()=>el.style.display='none',3300); }
async function api(path,opts={}){
 const resp=await fetch(API+path,{...opts,headers:{'X-User-Id':String(userId),...(opts.body instanceof FormData?{}:{'Content-Type':'application/json'}),...opts.headers}});
 let data=await resp.json().catch(()=>({}));
 if(!resp.ok)throw new Error(data.detail instanceof Array?data.detail[0]?.msg:(data.detail||'Request failed'));
 return data;
}
async function init(){try{
 const users=await api('/users'); $('#userSelect').innerHTML=users.map(u=>`<option value="${u.id}">${u.name}</option>`).join('');
 await reload();
 }catch(e){toast(e.message)} }
async function reload(selectedId=null){
 docs=await api('/documents');$('#docCount').textContent=docs.length;
 const list=$('#docList');list.replaceChildren();
 for(const d of docs){let b=document.createElement('button');b.className='doc-item'+(current?.id===d.id?' active':''); b.innerHTML='<span class="doc-icon">▤</span><span class="doc-info"><div class="doc-name"></div><div class="doc-sub"></div></span>';b.querySelector('.doc-name').textContent=d.title;b.querySelector('.doc-sub').textContent=d.is_owner?'Owned by you':'Shared by '+d.owner;b.onclick=()=>openDoc(d.id);list.append(b);}
 if(selectedId)await openDoc(selectedId);else if(current && !docs.some(d=>d.id===current.id))showEmpty();
}
function showEmpty(){current=null;$('#docPanel').hidden=true;$('#emptyState').hidden=false;$('#shareBtn').disabled=true;$('#currentCrumb').textContent='Documents';}
async function openDoc(id){
 const token=++requestToken;
 // Flush unsaved edits before navigating to another document.
 if(current?.is_owner && saveTimer)await saveNow();
 try{const d=await api('/documents/'+id);if(token!==requestToken)return;current=d;$('#emptyState').hidden=true;$('#docPanel').hidden=false;$('#titleInput').value=d.title;$('#editor').innerHTML=d.html;$('#titleInput').disabled=!d.is_owner;$('#editor').contentEditable=String(d.is_owner);document.querySelectorAll('[data-cmd]').forEach(b=>b.disabled=!d.is_owner);$('#accessLabel').textContent=d.is_owner?'Owned by you':'Shared by '+d.owner;$('#accessLabel').style.background=d.is_owner?'#eff8f3':'#f1efff';$('#docDate').textContent='Updated '+new Date(d.updated_at).toLocaleDateString();$('#currentCrumb').textContent=d.title;$('#shareBtn').disabled=!d.is_owner;$('#saveStatus').textContent=d.is_owner?'All changes saved':'Read only';countWords();await reloadListOnly();}catch(e){toast(e.message)}
}
async function reloadListOnly(){docs=await api('/documents');$('#docCount').textContent=docs.length;const list=$('#docList');list.replaceChildren();for(const d of docs){let b=document.createElement('button');b.className='doc-item'+(current?.id===d.id?' active':'');b.innerHTML='<span class="doc-icon">▤</span><span class="doc-info"><div class="doc-name"></div><div class="doc-sub"></div></span>';b.querySelector('.doc-name').textContent=d.title;b.querySelector('.doc-sub').textContent=d.is_owner?'Owned by you':'Shared by '+d.owner;b.onclick=()=>openDoc(d.id);list.append(b)}}
async function createDoc(){try{const d=await api('/documents',{method:'POST',body:JSON.stringify({title:'Untitled document',html:'<p></p>'})});await openDoc(d.id);$('#titleInput').focus();$('#titleInput').select()}catch(e){toast(e.message)}}
function scheduleSave(){if(!current?.is_owner)return;$('#saveStatus').textContent='Unsaved changes';clearTimeout(saveTimer);saveTimer=setTimeout(saveNow,650);}
async function saveNow(){if(!current?.is_owner)return;clearTimeout(saveTimer);saveTimer=null;const d=current;const payload={title:$('#titleInput').value,html:$('#editor').innerHTML};if(!payload.title.trim()){toast('Document title cannot be blank');return;}$('#saveStatus').textContent='Saving…';try{const saved=await api('/documents/'+d.id,{method:'PATCH',body:JSON.stringify(payload)});if(current?.id!==d.id)return;current=saved;$('#saveStatus').textContent='All changes saved';$('#currentCrumb').textContent=saved.title;await reloadListOnly()}catch(e){$('#saveStatus').textContent='Save failed — retry editing';toast(e.message)}}
function countWords(){const words=$('#editor').textContent.trim().split(/\s+/).filter(Boolean).length;$('#wordCount').textContent=words+' words'}
$('#newBtn').onclick=createDoc;$('#emptyNewBtn').onclick=createDoc;$('#titleInput').addEventListener('input',scheduleSave);$('#editor').addEventListener('input',()=>{scheduleSave();countWords()});
document.querySelectorAll('[data-cmd]').forEach(b=>{b.addEventListener('mousedown',e=>e.preventDefault());b.onclick=()=>{if(!current?.is_owner)return;$('#editor').focus();document.execCommand(b.dataset.cmd,false,b.dataset.value||null);scheduleSave();countWords()}});
$('#userSelect').onchange=async e=>{if(current?.is_owner&&saveTimer)await saveNow();userId=Number(e.target.value);const names={1:'Alex Morgan',2:'Jordan Lee'};$('#username').textContent=names[userId];$('#avatar').textContent=names[userId][0];showEmpty();await reload();};
$('#fileUpload').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{const data=new FormData();data.append('file',f);const doc=await api('/import',{method:'POST',body:data});await openDoc(doc.id);toast('Imported '+f.name)}catch(err){toast(err.message)}e.target.value=''};
$('#shareBtn').onclick=async()=>{if(!current?.is_owner)return;const users=await api('/users');const available=users.filter(u=>u.id!==userId);$('#recipient').innerHTML=available.map(u=>`<option value="${u.id}">${u.name}</option>`).join('');renderAccess();$('#modal').hidden=false};
function renderAccess(){const el=$('#accessList');el.replaceChildren();if(!current)return;const own=document.createElement('div');own.className='person';own.textContent=current.owner+' (Owner)';el.append(own);for(const p of current.shared_with){const row=document.createElement('div');row.className='person';row.textContent=p.name+' — Viewer';const b=document.createElement('button');b.textContent='Remove';b.onclick=async()=>{try{current=await api('/documents/'+current.id+'/share/'+p.id,{method:'DELETE'});renderAccess();toast('Access removed')}catch(e){toast(e.message)}};row.append(b);el.append(row)}}
$('#inviteBtn').onclick=async()=>{try{current=await api('/documents/'+current.id+'/share',{method:'POST',body:JSON.stringify({user_id:Number($('#recipient').value)})});renderAccess();toast('Shared successfully')}catch(e){toast(e.message)}};
function closeModal(){$('#modal').hidden=true}$('#modalClose').onclick=closeModal;$('#modalDone').onclick=closeModal;$('#modal').onclick=e=>{if(e.target===$('#modal'))closeModal()};
window.addEventListener('beforeunload',e=>{if(saveTimer){e.preventDefault();e.returnValue=''}});
init();
