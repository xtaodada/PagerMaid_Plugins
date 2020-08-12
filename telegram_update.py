import json, time, sys
from requests import get, post

token = str(sys.argv[1])

time.sleep(30)
main = json.loads(get("https://api.github.com/repos/xtaodada/PagerMaid_Plugins/commits/master").content)
push_content = {}
push_content['chat_id'] = '-1001441461877'
push_content['disable_web_page_preview'] = 'True'
push_content['parse_mode'] = 'markdown'
push_content['text'] = "#更新日志 #" + main['commit']['author'][
            'name'] + ' \n\n🔨 [' + main['sha'][0:7] + '](https://github.com/xtaodada/PagerMaid_Plugins/compare/' + \
                               main[
                                   'sha'] + '): ' + main['commit']['message']
url = 'https://api.telegram.org/bot' + token + '/sendMessage'
try:
    main_req = post(url, data=push_content)
except:
    pass
push_content['chat_id'] = '-1001319957857'
time.sleep(1)
try:
    main_req = get(url, data=push_content)
except:
    pass
print(main['sha'] + " ok！")
