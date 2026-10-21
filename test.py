# Headless test: python3 -m http.server 8765 (in this folder), then python3 test.py
import json, base64
from playwright.sync_api import sync_playwright
B='http://localhost:8765/index.html'
errs=[]
def banner(pg): return {c.get_attribute('data-team'): c.inner_text().replace('\n',' | ') for c in pg.query_selector_all('#banner .team')}
with sync_playwright() as p:
    br=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    def newpage(ctx):
        pg=ctx.new_page(); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e))); return pg
    # --- 1. migration from v1 localStorage ---
    old_people=[{'name':n,'team':'US' if n in ('Nicola','Lucia','Christy','Emily W') else 'China','color':'#123456'} for n in ['Xueyuan','Runrun','Weiwei','Steven','Nicola','Emily G','Lucia','Christy','Emily W','Sally','Muyi']]
    old_data={'people':old_people,'tasks':{'2026-10-12':{'Xueyuan':'MY ENTERED TASK'}},'delivery':{'2026-10-12':'D1'},'weekNotes':{},'stamps':{},'version':1}
    old_set={'skipWeekends':True,'headsUpMin':45,'sound':False,'deadlines':{'China':{'time':'18:00','tz':'Asia/Shanghai'},'US':{'time':'10:00','tz':'America/Los_Angeles'}}}
    ctx=br.new_context(viewport={'width':1280,'height':900},timezone_id='America/Los_Angeles')
    pg=newpage(ctx); pg.goto(B+'?view=settings')
    pg.evaluate("([d,s])=>{localStorage.clear();localStorage.setItem('storyverse.schedule.data.v1',d);localStorage.setItem('storyverse.schedule.settings.v1',s)}",[json.dumps(old_data),json.dumps(old_set)])
    pg.goto(B+'?now=2026-10-12T08:00:00Z&date=2026-10-12'); pg.wait_for_timeout(400)
    d=pg.evaluate("JSON.parse(localStorage.getItem('storyverse.schedule.data.v1'))"); s=pg.evaluate("JSON.parse(localStorage.getItem('storyverse.schedule.settings.v1'))")
    teams={x['name']:x['team'] for x in d['people']}
    print('MIGRATION: version',d['version'],s['version'],'| Runrun',teams['Runrun'],'| Kathy',teams.get('Kathy'),'| Emily Y',teams.get('Emily Y'),'| Nicola',teams['Nicola'],'| Xueyuan',teams['Xueyuan'])
    print('  kept task:',d['tasks']['2026-10-12'],'| kept headsUp:',s['headsUpMin'],'| teams:',[(t['id'],t['time'],t['tz']) for t in s['teams']],'| deadlines key gone:', 'deadlines' not in s)
    assert d['tasks']['2026-10-12']['Xueyuan']=='MY ENTERED TASK' and teams['Runrun']=='London' and teams['Kathy']=='Intern' and s['headsUpMin']==45
    print('  cards:',len(banner(pg))); ctx.close()
    # --- 2. fresh browser, deadline logic ---
    ctx=br.new_context(viewport={'width':1280,'height':900},timezone_id='America/Los_Angeles'); pg=newpage(ctx)
    pg.goto(B+'?now=2026-08-03T09:00:00Z&date=2026-08-03'); pg.wait_for_timeout(400)
    print('Xueyuan Aug3:', pg.eval_on_selector('.person[data-n="Xueyuan"] textarea','e=>e.value'))
    b=banner(pg); print('CARDS:',len(b)); [print(' 17:00 CN |',v) for v in b.values()]
    pg.fill('.person[data-n="Runrun"] textarea',''); pg.wait_for_timeout(700)
    pg.evaluate("__setNow('2026-08-03T09:45:00Z')"); pg.wait_for_timeout(300)
    print(' 17:45 CN London |',banner(pg)['London']); print('  toast:',pg.inner_text('#toastMsg').replace('\n',' ')); pg.click('#toastX')
    pg.evaluate("__setNow('2026-08-03T10:05:00Z')"); pg.wait_for_timeout(300)
    print(' 18:05 CN London |',banner(pg)['London']); print('  toast:',pg.inner_text('#toastMsg').replace('\n',' ')); pg.click('#toastX')
    pg.evaluate("__setNow('2026-08-03T16:45:00Z')"); pg.wait_for_timeout(300)
    print(' 09:45 LA Intern |',banner(pg)['Intern']); print('  toast:',pg.inner_text('#toastMsg').replace('\n',' ')); pg.click('#toastX')
    pg.evaluate("__setNow('2026-08-03T17:30:00Z')"); pg.wait_for_timeout(300)
    print(' 10:30 LA Intern |',banner(pg)['Intern']); print(' 10:30 LA US |',banner(pg)['US']); pg.click('#toastX')
    pg.fill('.person[data-n="Kathy"] textarea','Onboarding'); pg.click('.person[data-n="Emily Y"] .offbtn'); pg.wait_for_timeout(700)
    print(' after Kathy/Emily Y filled | Intern:',banner(pg)['Intern'])
    pg.fill('.person[data-n="Runrun"] textarea','社媒 Social'); pg.wait_for_timeout(700)
    pg.evaluate("__setNow('2026-08-03T16:40:00Z')"); pg.wait_for_timeout(300)
    if pg.is_visible('#toast'): pg.click('#toastX')
    pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(200)
    pg.screenshot(path='screenshot.png',full_page=True)
    pg.goto(B+'?now=2026-08-12T08:30:00Z&date=2026-08-12&view=week'); pg.wait_for_timeout(400)
    if pg.is_visible('#toast'): pg.click('#toastX')
    pg.screenshot(path='screenshot-week.png',full_page=True)
    pg.goto(B+'?view=settings'); pg.wait_for_timeout(300); pg.screenshot(path='screenshot-settings.png',full_page=True)
    m=newpage(br.new_context(viewport={'width':390,'height':844})); m.goto(B+'?now=2026-08-03T16:40:00Z&date=2026-08-03'); m.wait_for_timeout(300)
    if m.is_visible('#toast'): m.click('#toastX')
    m.screenshot(path='screenshot-mobile.png',full_page=True)
    # --- 3. projects + month view ---
    ctx=br.new_context(viewport={'width':1280,'height':900},timezone_id='America/Los_Angeles'); pg=newpage(ctx)
    pg.goto(B+'?now=2026-10-21T17:00:00Z&date=2026-10-21&view=projects'); pg.wait_for_timeout(300)
    assert pg.is_visible('#pEmpty')
    for nm,st,en in [('Alpha','2026-10-05','2026-10-20'),('Beta','2026-10-15','2026-11-10')]:
        pg.click('#pAdd'); r=pg.locator('.pj[data-pid]').last
        r.locator('[data-k=name]').fill(nm); r.locator('[data-k=start]').fill(st); r=pg.locator('.pj[data-pid]').last; r.locator('[data-k=end]').fill(en)
        r=pg.locator('.pj[data-pid]').last; r.locator('summary').click(); r.locator('[data-own="Xueyuan"]').check(); pg.click('h2')
    pg.wait_for_timeout(600)
    d=pg.evaluate("JSON.parse(localStorage.getItem('storyverse.schedule.data.v1'))")
    print('PROJECTS:',[(x['name'],x['start'],x['end'],x['owners']) for x in d['projects']]); assert len(d['projects'])==2 and d['projects'][1]['end']=='2026-11-10' and d['projects'][0]['owners']==['Xueyuan'] and d['version']==3
    pg.click('#tabs [data-v=month]'); pg.wait_for_timeout(200)
    bars=pg.locator('#mGrid .mbar'); print('OCT bars:',bars.count(), pg.inner_text('#mLabel')); assert bars.count()>=5
    pg.click('#mNext'); print('NOV bars:',pg.locator('#mGrid .mbar').count(), pg.inner_text('#mLabel')); assert pg.locator('#mGrid .mbar').count()==2
    pg.click('#mToday'); assert '10月' in pg.inner_text('#mLabel')
    pg.locator('#mGrid .mbar').first.click(); pg.wait_for_timeout(200); assert pg.is_visible('#v-projects')
    pg.once('dialog',lambda dl: dl.accept()); pg.locator('.pj[data-pid] [data-pdel]').first.click(); pg.wait_for_timeout(200)
    assert len(pg.evaluate("JSON.parse(localStorage.getItem('storyverse.schedule.data.v1')).projects"))==1; print('delete ok')
    ctx.close()
    # --- 4. cloud sync with mocked GitHub API ---
    srv={'doc':None,'sha':None,'n':0,'calls':[]}
    def gh(route):
        r=route.request; srv['calls'].append((r.method,r.headers.get('authorization')))
        assert 'storyverse-schedule-data/contents/schedule.json' in r.url and 'storyverse-hr' not in r.url
        if r.method=='GET':
            if srv['doc'] is None: return route.fulfill(status=404,json={'message':'Not Found'})
            return route.fulfill(json={'sha':srv['sha'],'content':base64.b64encode(srv['doc'].encode()).decode()})
        b=json.loads(r.post_data)
        if b.get('sha')!=srv['sha']: return route.fulfill(status=409,json={'message':'sha mismatch'})
        srv['n']+=1; srv['sha']='s%d'%srv['n']; srv['doc']=base64.b64decode(b['content']).decode()
        return route.fulfill(status=201 if srv['n']==1 else 200,json={'content':{'sha':srv['sha']}})
    ctx=br.new_context(viewport={'width':1280,'height':900},accept_downloads=True); ctx.route('https://api.github.com/**',gh); pg=newpage(ctx)
    pg.on('dialog',lambda dl: dl.accept())
    pg.goto(B+'?view=projects'); pg.wait_for_timeout(300)
    assert pg.inner_text('#syncState')=='本地' and pg.inner_text('#syncLogin')=='登录' and not srv['calls']; print('SYNC logged out: no API calls')
    pg.click('#syncLogin'); pg.fill('#tok','TESTTOKEN'); pg.click('#tokGo'); pg.wait_for_timeout(600)
    assert srv['n']==1 and json.loads(srv['doc'])['data']['people'], srv; print('SYNC first upload ok, state:',pg.inner_text('#syncState'))
    assert pg.evaluate("localStorage.getItem('sv_schedule_token')")=='TESTTOKEN' and pg.evaluate("localStorage.getItem('sv_payroll_token')") is None
    pg.uncheck('#syncAuto'); pg.click('#pAdd'); pg.locator('.pj[data-pid] [data-k=name]').last.fill('Synced'); pg.locator('.pj[data-pid] [data-k=name]').last.press('Tab'); pg.wait_for_timeout(600)
    assert pg.inner_text('#syncState')=='未保存'; pg.click('#syncSave'); pg.wait_for_timeout(500)
    assert pg.inner_text('#syncState')=='已同步' and json.loads(srv['doc'])['data']['projects'][0]['name']=='Synced'; print('SYNC manual save ok')
    pg.check('#syncAuto'); pg.locator('.pj[data-pid] [data-k=notes]').last.fill('auto'); pg.locator('.pj[data-pid] [data-k=notes]').last.press('Tab'); pg.wait_for_timeout(5000)
    assert json.loads(srv['doc'])['data']['projects'][0]['notes']=='auto'; print('SYNC auto-save ok')
    # someone else saves -> our save conflicts
    d=json.loads(srv['doc']); d['data']['projects'][0]['name']='OtherPerson'; srv['doc']=json.dumps(d); srv['sha']='other'
    pg.uncheck('#syncAuto'); pg.locator('.pj[data-pid] [data-k=name]').last.fill('Mine'); pg.locator('.pj[data-pid] [data-k=name]').last.press('Tab'); pg.wait_for_timeout(600)
    with pg.expect_download() as dl: pg.click('#syncSave')
    pg.wait_for_timeout(600)
    print('SYNC conflict state:',pg.inner_text('#syncState'),'| backup:',dl.value.suggested_filename)
    assert '冲突' in pg.inner_text('#syncState') and json.loads(srv['doc'])['data']['projects'][0]['name']=='OtherPerson'
    assert pg.locator('.pj[data-pid] [data-k=name]').last.input_value()=='OtherPerson'
    # reopen -> loads from repo
    pg2=newpage(ctx); pg2.goto(B+'?view=projects'); pg2.wait_for_timeout(600); assert pg2.locator('.pj[data-pid] [data-k=name]').last.input_value()=='OtherPerson' and pg2.inner_text('#syncState')=='已同步'
    assert all(a=='Bearer TESTTOKEN' for _,a in srv['calls'])
    pg2.click('#syncLogin'); assert pg2.inner_text('#syncState')=='本地' and pg2.evaluate("localStorage.getItem('sv_schedule_token')") is None; print('SYNC reload + logout ok')
    ctx.close()
    br.close()
print('ERRORS:',errs)
