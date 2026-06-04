#!/usr/bin/env python3
"""
gmo_badges.csv + badges.json → index.html を生成するスクリプト
GitHub Actions から呼ばれる
"""
import csv
import json
import sys
import os
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

def load_badges_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def load_csv(path):
    """
    CSVフォーマット: 部署,氏名,読み,社員番号(?),バッジ一覧(|区切り),...
    ヘッダー行は 氏名 or 部署 を含む行をスキップ
    """
    members = []
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0 and any(h in ','.join(row) for h in ['氏名', '部署', '本部']):
                continue
            if len(row) < 2:
                continue
            dept = row[0].strip().strip('"')
            name = row[1].strip().strip('"')
            if not name:
                continue
            badge_str = row[4].strip().strip('"') if len(row) > 4 else ''
            badges = [b.strip() for b in badge_str.split('|') if b.strip()] if badge_str else []
            join_date = row[5].strip().strip('"') if len(row) > 5 else ''
            members.append({'dept': dept, 'name': name, 'badges': badges, 'join_date': join_date})
    return members

def build_html(members, badge_images):
    now = datetime.now(JST).strftime('%Y年%m月%d日 %H:%M')
    members_json = json.dumps(members, ensure_ascii=False)
    badge_images_json = json.dumps(badge_images, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GMOコマース バッジ取得状況</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Noto Sans JP',sans-serif;background:#f4f5f7;color:#1a1a2e;font-size:13px;min-height:100vh;}}
.header{{background:#1a1a2e;color:#fff;padding:18px 28px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 2px 12px rgba(0,0,0,0.2);}}
.header-left{{display:flex;align-items:center;gap:10px;}}
.header-dot{{width:12px;height:12px;border-radius:50%;background:#4ECDC4;}}
.header-title{{font-size:16px;font-weight:700;}}
.header-sub{{font-size:11px;color:#8899aa;margin-top:2px;}}
.header-btns{{display:flex;gap:8px;}}
.btn{{font-size:12px;padding:7px 14px;border-radius:6px;cursor:pointer;border:none;font-family:inherit;font-weight:500;display:flex;align-items:center;gap:6px;transition:all 0.15s;}}
.btn-import{{background:#1e3a5f;color:#4ECDC4;border:1px solid #4ECDC4;}}
.btn-import:hover{{background:#2a4d7a;}}
.btn-export{{background:#1a1a2e;color:#fff;border:1px solid #444;}}
.btn-export:hover{{background:#2d2d4e;}}
.main{{padding:20px 24px;}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px;}}
.stat-card{{background:#fff;border-radius:12px;padding:16px 20px;border:1px solid #e8eaed;box-shadow:0 1px 4px rgba(0,0,0,0.05);}}
.stat-label{{font-size:11px;color:#888;margin-bottom:8px;}}
.stat-value{{font-size:28px;font-weight:700;line-height:1;}}
.stat-value.green{{color:#10b981;}}
.stat-value.red{{color:#ef4444;}}
.stat-value.blue{{color:#3b82f6;}}
.progress-wrap{{height:4px;background:#e8eaed;border-radius:2px;margin-top:8px;}}
.progress-bar{{height:4px;background:linear-gradient(90deg,#4ECDC4,#10b981);border-radius:2px;transition:width 0.5s ease;}}
.adv-alert{{background:#fff5f5;border:1px solid #fecaca;border-radius:12px;padding:14px 18px;margin-bottom:16px;}}
.adv-alert-title{{font-weight:700;color:#dc2626;font-size:12px;margin-bottom:8px;}}
.adv-tag{{display:inline-block;background:#fee2e2;color:#dc2626;border-radius:4px;padding:2px 8px;margin:2px;font-size:11px;}}
.controls{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px;background:#fff;padding:12px 16px;border-radius:12px;border:1px solid #e8eaed;box-shadow:0 1px 4px rgba(0,0,0,0.05);}}
.controls select,.controls input{{font-size:12px;padding:7px 12px;border-radius:6px;border:1px solid #e0e0e0;background:#f9fafb;color:#1a1a2e;outline:none;font-family:inherit;}}
.controls select:focus,.controls input:focus{{border-color:#4ECDC4;background:#fff;}}
.count-label{{color:#888;font-size:11px;}}
.table-wrap{{overflow-x:auto;background:#fff;border-radius:12px;border:1px solid #e8eaed;box-shadow:0 1px 4px rgba(0,0,0,0.05);}}
table{{width:100%;border-collapse:collapse;font-size:12px;}}
thead th{{background:#1a1a2e;color:#ccc;padding:10px 8px;font-weight:500;white-space:nowrap;position:sticky;top:0;z-index:2;text-align:center;}}
thead th.col-dept{{text-align:left;position:sticky;left:0;z-index:3;background:#1a1a2e;min-width:100px;padding-left:16px;}}
thead th.col-name{{text-align:left;position:sticky;left:100px;z-index:3;background:#1a1a2e;min-width:90px;}}
thead th.adv-col{{background:#0a3d35;color:#4ECDC4;}}
.badge-col-header{{min-width:44px;padding:6px 4px;vertical-align:bottom;}}
.dept-row td{{background:#eef2ff;font-weight:700;padding:8px 16px;font-size:12px;color:#1a1a2e;border-top:2px solid #e0e4ff;}}
.dept-pct{{display:inline-block;background:#1a1a2e;color:#4ECDC4;border-radius:4px;padding:1px 8px;font-size:10px;margin-left:8px;font-weight:500;}}
.member-row td{{padding:7px 8px;border-bottom:1px solid #f0f0f0;text-align:center;vertical-align:middle;}}
.member-row:hover td{{background:#f0fffe;}}
.member-row.no-adv td{{background:#fff8f8;}}
.col-dept-cell{{text-align:left!important;padding-left:16px!important;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;position:sticky;left:0;background:inherit;}}
.col-name-cell{{text-align:left!important;padding-left:8px!important;position:sticky;left:100px;background:inherit;min-width:90px;white-space:nowrap;}}
.badge-img{{width:28px;height:28px;border-radius:50%;vertical-align:middle;}}
.dot-yes{{display:inline-block;width:18px;height:18px;border-radius:50%;background:#10b981;line-height:18px;color:#fff;font-size:11px;}}
.dot-adv{{display:inline-block;width:18px;height:18px;border-radius:50%;background:#4ECDC4;line-height:18px;color:#fff;font-size:11px;}}
.dot-no{{display:inline-block;width:18px;height:18px;border-radius:50%;background:#f0f0f0;}}
.update-time{{font-size:10px;color:#8899aa;margin-top:2px;}}
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <div class="header-dot"></div>
    <div>
      <div class="header-title">GMOコマース バッジ取得状況</div>
      <div class="header-sub">虎の穴 Learning Badge Tracker</div>
      <div class="update-time">最終更新: {now}</div>
    </div>
  </div>
  <div class="header-btns">
    <label class="btn btn-import">📥 CSVを更新<input type="file" accept=".csv" style="display:none" onchange="importCSV(this)"></label>
    <button class="btn btn-export" onclick="downloadCSV()">📤 CSVエクスポート</button>
  </div>
</div>
<div class="main">
  <div class="stats">
    <div class="stat-card">
      <div class="stat-label">総社員数</div>
      <div class="stat-value blue" id="s-total">-</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">アドバンス取得</div>
      <div class="stat-value green" id="s-adv">-</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">アドバンス未取得</div>
      <div class="stat-value red" id="s-no">-</div>
      <div class="progress-wrap"><div class="progress-bar" id="s-bar" style="width:0%"></div></div>
    </div>
    <div class="stat-card">
      <div class="stat-label">アドバンス取得率</div>
      <div class="stat-value" id="s-pct">-%</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">部署数</div>
      <div class="stat-value" id="s-dept">-</div>
    </div>
  </div>
  <div class="adv-alert" id="advAlert" style="display:none">
    <div class="adv-alert-title">⚠️ アドバンス未取得メンバー</div>
    <div id="advAlertNames"></div>
  </div>
  <div class="controls">
    <select id="deptFilter" onchange="render()"></select>
    <input type="text" id="nameSearch" placeholder="氏名で検索..." oninput="render()">
    <select id="advFilter" onchange="render()">
      <option value="">全員</option>
      <option value="yes">アドバンス取得済み</option>
      <option value="no">アドバンス未取得</option>
    </select>
    <select id="sortSel" onchange="render()">
      <option value="dept">組織図順</option>
      <option value="adv-desc">アドバンス取得者優先</option>
      <option value="badge-desc">バッジ数↓</option>
      <option value="name">氏名順</option>
      <option value="join-asc">入社順（古い順）</option>
      <option value="join-desc">入社順（新しい順）</option>
    </select>
    <span class="count-label" id="countLabel"></span>
  </div>
  <div class="table-wrap">
    <table id="mainTable">
      <thead id="thead"></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</div>
<script>
var BADGE_IMAGES = {badge_images_json};
var INITIAL_MEMBERS = {members_json};
var DEPT_ORDER = [
  '代表取締役社長','常務取締役',
  '営業統括本部','営業第1本部','営業第2本部','パートナー推進本部','営業推進本部',
  'オペレーション本部',
  '企画開発統括本部','商品企画本部','開発本部',
  '経営企画統括本部','経営企画本部',
  'コーポレート統括本部','管理本部','人事本部',
  '内部監査室','監査役','会議室アカウント'
];
function getDeptOrder(dept){{
  for(var i=0;i<DEPT_ORDER.length;i++){{
    if(dept.includes(DEPT_ORDER[i]))return i;
  }}
  return 99;
}}
var members=INITIAL_MEMBERS.slice();
var allBadgeCols=[];
var BADGE_ORDER=['虎の穴｜アドバンス','虎の穴｜ベーシック','虎の穴｜マスター','虎の穴｜RPA基礎','虎の穴｜RPA応用','虎の穴｜汎用生成AIセキュリティ基礎','虎の穴｜画像生成AI入門','虎の穴｜Slackワークフロー','虎の穴｜Power Automate クラウド版','虎の穴｜Dify入門','虎の穴｜Google App Script（GAS）入門','虎の穴｜Google Apps Script（GAS）応用','虎の穴｜ConoHa AI Canvas','虎の穴｜Chrome拡張機能開発','虎の穴｜バイブDX基礎','虎の穴｜Adobe Express 入門','虎の穴｜AI動画編集基礎（CapCut）','虎の穴｜Claude基礎（AnthropicAcademy）'];
function short(b){{return b.replace(/虎の穴[｜|]/,'').replace('（AnthropicAcademy）','').replace('（CapCut）','').replace('クラウド版','');}}
function hasBadge(m,b){{if(!m.badges)return false;return m.badges.some(function(mb){{var a=mb.trim().replace(/[|]/g,'｜').replace(/[\s]/g,'');var c=b.trim().replace(/[|]/g,'｜').replace(/[\s]/g,'');return a===c||a.includes(c.replace('虎の穴｜',''))||c.includes(a.replace('虎の穴｜',''));}});}}
function hasAdv(m){{return hasBadge(m,'虎の穴｜アドバンス');}}
function getBadgeImg(name){{var keys=Object.keys(BADGE_IMAGES);for(var i=0;i<keys.length;i++){{var k=keys[i];if(k.replace(/[\s]/g,'')===name.replace(/[\s]/g,'')||name.includes(k.replace('虎の穴｜',''))||k.includes(name.replace('虎の穴｜',''))){{return '<img src="'+BADGE_IMAGES[k]+'" class="badge-img" title="'+name+'">';}}}}var isAdv=name.includes('アドバンス');return '<span class="'+(isAdv?'dot-adv':'dot-yes')+'">✓</span>';}}
function rebuildCols(){{var cols={{}};members.forEach(function(m){{if(m.badges)m.badges.forEach(function(b){{if(b)cols[b]=1;}});}});BADGE_ORDER.forEach(function(b){{cols[b]=1;}});allBadgeCols=Object.keys(cols).sort(function(a,b2){{var ai=BADGE_ORDER.findIndex(function(x){{return x.replace(/[\s]/g,'')===a.replace(/[\s]/g,'');}});var bi=BADGE_ORDER.findIndex(function(x){{return x.replace(/[\s]/g,'')===b2.replace(/[\s]/g,'');}});if(ai<0)ai=99;if(bi<0)bi=99;return ai-bi;}});}}
function getDepts(){{
  var depts=[...new Set(members.map(function(m){{return m.dept;}}).filter(Boolean))];
  depts.sort(function(a,b){{return getDeptOrder(a)-getDeptOrder(b);}});
  return depts;
}}
function updateDeptFilter(){{var sel=document.getElementById('deptFilter');var cur=sel.value;sel.innerHTML='<option value="">すべての本部</option>';getDepts().forEach(function(d){{var o=document.createElement('option');o.value=d;o.textContent=d;if(d===cur)o.selected=true;sel.appendChild(o);}});}}
function getFiltered(){{var dept=document.getElementById('deptFilter').value;var name=document.getElementById('nameSearch').value.toLowerCase();var adv=document.getElementById('advFilter').value;return members.filter(function(m){{if(dept&&m.dept!==dept)return false;if(name&&!m.name.toLowerCase().includes(name))return false;if(adv==='yes'&&!hasAdv(m))return false;if(adv==='no'&&hasAdv(m))return false;return true;}});}}
function getSorted(arr){{var key=document.getElementById('sortSel').value;var copy=arr.slice();if(key==='adv-desc'){{copy.sort(function(a,b){{return(hasAdv(b)?1:0)-(hasAdv(a)?1:0)||b.badges.length-a.badges.length;}});}}else if(key==='badge-desc'){{copy.sort(function(a,b){{return b.badges.length-a.badges.length;}});}}else if(key==='name'){{copy.sort(function(a,b){{return a.name.localeCompare(b.name,'ja');}});}}else if(key==='join-asc'){{copy.sort(function(a,b){{return(a.join_date||'').localeCompare(b.join_date||'');}});}}else if(key==='join-desc'){{copy.sort(function(a,b){{return(b.join_date||'').localeCompare(a.join_date||'');}});}}else{{copy.sort(function(a,b){{var od=getDeptOrder(a.dept)-getDeptOrder(b.dept);if(od!==0)return od;return a.dept.localeCompare(b.dept,'ja')||a.name.localeCompare(b.name,'ja');}});}}return copy;}}
function render(){{
  var f=getFiltered();
  var noAdv=f.filter(function(m){{return!hasAdv(m);}});
  var advCount=f.length-noAdv.length;
  var pct=f.length>0?Math.round(advCount/f.length*100):0;
  var deptCount=[...new Set(f.map(function(m){{return m.dept;}}).filter(Boolean))].length;
  document.getElementById('s-total').textContent=f.length;
  document.getElementById('s-adv').textContent=advCount;
  document.getElementById('s-no').textContent=noAdv.length;
  document.getElementById('s-pct').textContent=pct+'%';
  document.getElementById('s-bar').style.width=pct+'%';
  document.getElementById('s-dept').textContent=deptCount;
  document.getElementById('countLabel').textContent=f.length+'人表示中';
  var al=document.getElementById('advAlert');
  if(noAdv.length>0&&document.getElementById('advFilter').value!=='yes'){{al.style.display='block';document.getElementById('advAlertNames').innerHTML=noAdv.map(function(m){{return'<span class="adv-tag">'+m.name+'</span>';}}).join('');}}else{{al.style.display='none';}}
  var thHtml='<tr><th class="col-dept">本部</th><th class="col-name">氏名</th>';
  allBadgeCols.forEach(function(b){{var isAdv=b.includes('アドバンス');var imgKey=Object.keys(BADGE_IMAGES).find(function(k){{return k.replace(/[\s]/g,'')===b.replace(/[\s]/g,'')||b.includes(k.replace('虎の穴｜',''))||k.includes(b.replace('虎の穴｜',''));}});var img=imgKey?'<img src="'+BADGE_IMAGES[imgKey]+'" style="width:28px;height:28px;border-radius:50%;display:block;margin:0 auto 3px;" title="'+b+'">':'';thHtml+='<th class="badge-col-header'+(isAdv?' adv-col':'')+'" title="'+b+'">'+img+'<div style="writing-mode:vertical-rl;font-size:9px;line-height:1.2;">'+short(b)+'</div></th>';}});
  thHtml+='</tr>';
  document.getElementById('thead').innerHTML=thHtml;
  var sorted=getSorted(f);
  var tbHtml='';
  var byDept={{}};var deptKeys=[];
  sorted.forEach(function(m){{var d=m.dept||'(未設定)';if(!byDept[d]){{byDept[d]=[];deptKeys.push(d);}}byDept[d].push(m);}});
  deptKeys.forEach(function(dept){{var grp=byDept[dept];var da=grp.filter(hasAdv).length;var dpct=Math.round(da/grp.length*100);tbHtml+='<tr class="dept-row"><td colspan="'+(2+allBadgeCols.length)+'">'+dept+'<span class="dept-pct">'+da+'/'+grp.length+'人 '+dpct+'%</span></td></tr>';grp.forEach(function(m){{tbHtml+=memberRow(m);}});}});
  document.getElementById('tbody').innerHTML=tbHtml;
}}
function memberRow(m){{var adv=hasAdv(m);var html='<tr class="member-row'+(adv?'':' no-adv')+'"><td class="col-dept-cell">'+(m.dept.length>14?m.dept.substring(0,14)+'…':m.dept)+'</td><td class="col-name-cell">'+m.name+'</td>';allBadgeCols.forEach(function(b){{var has=hasBadge(m,b);html+='<td>';if(has)html+=getBadgeImg(b);else html+='<span class="dot-no"></span>';html+='</td>';}});return html+'</tr>';}}
function importCSV(input){{var file=input.files[0];if(!file)return;var reader=new FileReader();reader.onload=function(e){{var lines=e.target.result.split('\\n').filter(function(l){{return l.trim();}});members=[];lines.forEach(function(line,idx){{if(idx===0&&(line.includes('氏名')||line.includes('部署')))return;var cols=line.split(',').map(function(c){{return c.trim().replace(/^"|"$/g,'');}});if(cols.length<2)return;var dept=cols[0],name=cols[1];if(!name)return;var badgeStr=cols[4]||'';var badges=badgeStr?badgeStr.split('|').map(function(b){{return b.trim();}}).filter(Boolean):[];members.push({{dept:dept,name:name,badges:badges}});}});rebuildCols();updateDeptFilter();render();alert(members.length+'件に更新しました！');}};reader.readAsText(file,'UTF-8');input.value='';}}
function downloadCSV(){{var rows=[['本部','氏名'].concat(allBadgeCols)];members.forEach(function(m){{var row=[m.dept,m.name];allBadgeCols.forEach(function(b){{row.push(hasBadge(m,b)?1:0);}});rows.push(row);}});var txt=rows.map(function(r){{return r.map(function(c){{return'"'+String(c).replace(/"/g,'""')+'"';}}).join(',');}}).join('\\n');var blob=new Blob(['\\uFEFF'+txt],{{type:'text/csv'}});var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='gmo_badges_full.csv';a.click();}}
rebuildCols();updateDeptFilter();render();
</script>
</body>
</html>'''
    return html

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, 'gmo_badges.csv')
    badges_path = os.path.join(base, 'badges.json')
    out_path = os.path.join(base, 'index.html')

    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} が見つかりません", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(badges_path):
        print(f"ERROR: {badges_path} が見つかりません", file=sys.stderr)
        sys.exit(1)

    print(f"Loading badges from {badges_path}...")
    badge_images = load_badges_json(badges_path)
    print(f"  → {len(badge_images)} badges loaded")

    print(f"Loading members from {csv_path}...")
    members = load_csv(csv_path)
    print(f"  → {len(members)} members loaded")

    print(f"Generating index.html...")
    html = build_html(members, badge_images)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  → {out_path} written ({len(html):,} bytes)")

if __name__ == '__main__':
    main()
