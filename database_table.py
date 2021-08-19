import json
import requests

def api_call(method, url, data=None, headers=None):
    if method == 'POST':
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            # Additional code will only run if the request is successful
            return response

        except requests.exceptions.HTTPError as error:
            print(error)
            # This code will run if there is a 404 error.

    if method == 'GET':
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            # Additional code will only run if the request is successful
            return response

        except requests.exceptions.HTTPError as error:
            print(error)
            # This code will run if there is a 404 error.

def get_token_and_projectID(username, password):
    obj = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "name": username,
                        "password": password,
                        "domain": {
                            "name": username
                        }
                    }
                }
            },
            "scope": {
                "project": {
                    "name": "ap-southeast-2"
                }
            }
        }
    }
    response = api_call('POST',
                        'https://iam.ap-southeast-2.myhuaweicloud.com/v3/auth/tokens', data=obj)
    return response

def get_RDS():
    username = input('Huawei cloud username: ')
    password = input('Huawei cloud password: ')
    response = get_token_and_projectID(username, password)
    token = response.headers['X-Subject-Token']
    catalog = response.json()['token']['catalog']
    database = {
        '1': 'SQLServer',
        '2': 'PostgreSQL',
        '3': 'MySQL'
    }
    [print(key,':',value) for key, value in database.items()]
    selected = database[input('select: ')]
    text = ''
    for endpoint in catalog:
        if endpoint['name'] == 'rdsv3':
            my_headers = {'X-Auth-Token': token}
            response = api_call('GET',
                                endpoint['endpoints'][0]['url']+'/flavors/' + selected, headers=my_headers)
            flavors = response.json()['flavors']
            text = f'Database {selected}\n| CODE | VCPUs |  RAM |  MODE   | VERSION |\n| --- | --: | --: | :--: | :-- | \n'
            for flavor in flavors:
                text += f"{flavor['spec_code']} | {flavor['vcpus']} | {flavor['ram']} | {flavor['instance_mode']} |"
                text += ", ".join(flavor['version_name']) + '\n'
            break
    filename = f'{selected}_table.md'
    print(f'Output: {filename}')
    with open(filename, 'w', encoding='utf-8') as outfile:
        outfile.write(text)

get_RDS()
