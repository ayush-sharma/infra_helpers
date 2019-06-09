from requests_oauthlib import OAuth2Session
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit
import csv
import json


class ClientSecrets:

    client_id = None
    client_secret = None
    redirect_uris = [
        'https://localhost'
    ]
    auth_uri = 'https://bitbucket.org/site/oauth2/authorize'
    token_uri = 'https://bitbucket.org/site/oauth2/access_token'
    server_base_uri = 'https://api.bitbucket.org/'


def get_all_repos(BBClient, next_page_url):

    data = []

    response = BBClient.get(next_page_url)

    try:

        response_dict = json.loads(response.content)

    except Exception, e:

        print(str(e))

    if 'values' in response_dict:

        for repo in response_dict['values']:

            data.append({

                'uuid': repo['uuid'],
                'name': repo['name'],
                'pr_url': repo['links']['pullrequests']['href'],
                'lang': repo['language'],
                'updated_on': repo['updated_on'],
                'size': repo['size'],
                'slug': repo['slug']
            })

    if 'next' in response_dict:

        data += get_all_repos(BBClient=BBClient,
                              next_page_url=response_dict['next'])

    return data


def get_all_pipelines(BBClient, next_page_url):

    data = []

    response = BBClient.get(next_page_url)

    try:

        response_dict = json.loads(response.content)

    except Exception, e:

        print(str(e))

    if 'values' in response_dict:

        for repo in response_dict['values']:

            data.append({

                'uuid': repo['uuid'],
                'repo': repo['repository']['name'],
                'state': repo['state']['result']['name'],
                'build_number': repo['build_number'],
                'creator': repo['creator']['display_name'] + '/' + repo['creator']['username'],
                'target_type': repo['target']['ref_type'] if 'ref_type' in repo['target'] else '',
                'target_name': repo['target']['ref_name'] if 'ref_name' in repo['target'] else '',
                'trigger': str(repo['trigger']['name']),
                'duration': repo['duration_in_seconds'],
                'created_on': repo['created_on'],
                'completed_on': repo['completed_on']
            })

    if 'next' in response_dict:

        data += get_all_pipelines(BBClient=BBClient,
                                  next_page_url=response_dict['next'])

    elif 'page' in response_dict and 'pagelen' in response_dict and response_dict['page'] < response_dict['pagelen']:

        """ If next page URL does not exist, assemble next page URL manually.
        """
        scheme, netloc, path, query_string, fragment = urlsplit(next_page_url)
        query_params = parse_qs(query_string)

        query_params['page'] = [response_dict['page'] + 1]
        new_query_string = urlencode(query_params, doseq=True)

        next_page_url = urlunsplit(
            (scheme, netloc, path, new_query_string, fragment))

        data += get_all_pipelines(BBClient=BBClient,
                                  next_page_url=next_page_url)

    return data


if __name__ == '__main__':

    # Initialize Bitbucket secrets
    c = ClientSecrets()
    c.client_id = ''
    c.client_secret = ''
    account_id = ''

    # Fetch a request token
    BBClient = OAuth2Session(c.client_id)

    # Redirect user to Bitbucket for authorization
    authorization_url = BBClient.authorization_url(c.auth_uri)
    print('Please go here and authorize: {}'.format(authorization_url[0]))

    # Get the authorization verifier code from the callback url
    redirect_response = raw_input('Paste the full redirect URL here:')

    # Fetch the access token
    BBClient.fetch_token(
        c.token_uri,
        authorization_response=redirect_response,
        username=c.client_id,
        password=c.client_secret,
        client_secret=c.client_secret)

    repo_list = get_all_repos(
        BBClient, next_page_url=c.server_base_uri + '2.0/repositories/' + account_id)

    with open('repos.csv', 'wb') as csv_file:

        print('> Saving repos report to file...')

        writer = csv.DictWriter(csv_file, repo_list[0].keys())
        writer.writeheader()
        writer.writerows(repo_list)

    print('> Repo report saved.')
    
    pipelines_list = []
    for repo in repo_list:

        pipelines_list += get_all_pipelines(BBClient, next_page_url=c.server_base_uri +
                                            '2.0/repositories/' + account_id + '/' + repo['slug'] + '/pipelines/?page=1')

    with open('pipelines.csv', 'wb') as csv_file:

        print('> Saving pipelines list to file...')

        writer = csv.DictWriter(csv_file, pipelines_list[0].keys())
        writer.writeheader()
        writer.writerows(pipelines_list)
    
    print('> Pipelines report saved.')