from datetime import datetime
import requests

def gitlab_get_issue(url, token, issue):
    ret = None
    error = None
    # https://docs.gitlab.com/ee/api/issues.html#new-issue
    requests.packages.urllib3.disable_warnings()
    if not url.endswith('/issues'):
        url += '/issues'
    if isinstance(issue, dict):
        url += '/%s' % issue.get('iid')
    else:
        url += '/%s' % issue
    headers = {'PRIVATE-TOKEN': token}
    params = {}

    try:
        response = requests.get(url, headers=headers, params=params)
        if (response.status_code >= 200) and (response.status_code < 300):
            h = response.headers.get('content-type')
            if h and ';' in h:
                h, _ = h.split(';',1)
            if h is not None and h == 'application/json':
                response.encoding = 'utf-8-sig' #fix encoding BOM error
                ret = response.json()
        else:
            error = 'HTTP Error %s: %s' % (response.status_code, response.reason)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        error = e
    return ret, error

def gitlab_get_issue_list(url, token, filter=None):
    ret = None
    error = None
    requests.packages.urllib3.disable_warnings()
    if not url.endswith('/issues'):
        url += '/issues'
    page = 0
    params = {}
    if filter:
        if filter.get('labels'):
            params['labels'] =  ','.join(filter.get('labels', []))
        if filter.get('state'):
            params['state'] =  filter.get('state')
    ret = []
    headers = {'PRIVATE-TOKEN': token}
    missing_pages = True
    while missing_pages:
        page += 1
        params['page'] = str(page)
        try:
            response = requests.get(url, headers=headers, params=params)
            if (response.status_code >= 200) and (response.status_code < 300):
                h = response.headers.get('content-type')
                if h and ';' in h:
                    h, _ = h.split(';',1)
                if h is not None and h == 'application/json':
                    response.encoding = 'utf-8-sig' #fix encoding BOM error
                    issue_result = response.json()
                    if not issue_result:
                        missing_pages = False
                    ret.extend(issue_result)
            else:
                error = 'HTTP Error %s: %s' % (response.status_code, response.reason)
                missing_pages = False
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            error = e
            missing_pages = False
    return ret, error


def gitlab_create_issue(url, token, issue):
    ret = None
    error = None
    # https://docs.gitlab.com/ee/api/issues.html#new-issue
    requests.packages.urllib3.disable_warnings()
    if not url.endswith('/issues'):
        url += '/issues'
    headers = {'PRIVATE-TOKEN': token}
    params = {
        'title': issue.get('title', None), 
        'description': issue.get('description', ''), 
        'labels': ','.join(issue.get('labels', [])), 
        'issue_type': issue.get('issue_type', 'issue'), 
        'confidential': '1' if issue.get('confidential', False) else '0'
         }
    if 'iid' in issue:
        params['iid'] = issue.get('iid')
    if 'created_at' in issue:
        t = issue.get('created_at')
        if isinstance(t, datetime):
            params['created_at'] = t.isoformat()
        else:
            params['created_at'] = t
        
    try:
        response = requests.post(url, headers=headers, params=params)
        if (response.status_code >= 200) and (response.status_code < 300):
            h = response.headers.get('content-type')
            if h and ';' in h:
                h, _ = h.split(';',1)
            if h is not None and h == 'application/json':
                response.encoding = 'utf-8-sig' #fix encoding BOM error
                issue_result = response.json()
                ret = issue_result
        else:
            error = 'HTTP Error %s: %s' % (response.status_code, response.reason)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        error = e
    return ret, error

def gitlab_edit_issue(url, token, issue):
    ret = False
    error = None
    # https://docs.gitlab.com/ee/api/issues.html#new-issue
    requests.packages.urllib3.disable_warnings()
    if not url.endswith('/issues'):
        url += '/issues'
    url += '/%s' % issue.get('iid')
    headers = {'PRIVATE-TOKEN': token}
    params = {}
    if not issue.get('title', None):
        params['title'] = issue.get('title', None)
    if not issue.get('description', None):
        params['description'] = issue.get('description', None)
    if not issue.get('labels', None):
        params['labels'] = ','.join(issue.get('labels', []))

    try:
        response = requests.put(url, headers=headers, params=params)
        if (response.status_code >= 200) and (response.status_code < 300):
            ret = True
        else:
            error = 'HTTP Error %s: %s' % (response.status_code, response.reason)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        error = e
    return ret, error

def gitlab_delete_issue(url, token, issue):
    ret = False
    error = None
    # https://docs.gitlab.com/ee/api/issues.html#new-issue
    requests.packages.urllib3.disable_warnings()
    if not url.endswith('/issues'):
        url += '/issues'
    if isinstance(issue, dict):
        url += '/%s' % issue.get('iid')
    else:
        url += '/%s' % issue
    headers = {'PRIVATE-TOKEN': token}
    params = {}

    try:
        response = requests.delete(url, headers=headers, params=params)
        if (response.status_code >= 200) and (response.status_code < 300):
            ret = True
        else:
            error = 'HTTP Error %s: %s' % (response.status_code, response.reason)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        error = e
    return ret, error

def gitlab_delete_multiple_issues(url, token, filter=None):
    ret = False
    list, error = gitlab_get_issue_list(url, token, filter=filter)
    if not list:
        return ret, error
    ret = True
    for issue in list:
        ret, error = gitlab_delete_issue(url, token, issue)
        if not ret:
            break
    return ret, error

def main():
    import argparse
    parser = argparse.ArgumentParser(description='GitLab direct access')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='enable verbose output of this script.')
    parser.add_argument('url')
    parser.add_argument('token')
    parser.add_argument('action', choices=['list', 'delete-all'])
    parser.add_argument('args', nargs='*')

    args = parser.parse_args()

    if args.action == 'list':
        list, error = gitlab_get_issue_list(args.url, args.token, None)
        if not list and error:
            print('Error %s' % error)
        else:
            if not list:
                print('No Issues')
            else:
                for issue in list:
                    print('[%i]: %s' % (issue.get('iid'), issue))
    elif args.action == 'delete-all':
        ret, error = gitlab_delete_multiple_issues(args.url, args.token, None)
        if not ret and error:
            print('Error %s' % error)
        else:
            print('Result: %s' % ret)
    else:
        print('Unknown action %s' % args.action)

    return 0


if __name__ == "__main__":
    import sys
    # execute only if run as a script
    sys.exit(main())
