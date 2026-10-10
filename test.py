# Headless test: python3 -m http.server 8765 (in this folder), then python3 test.py
import json
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
    br.close()
print('ERRORS:',errs)
