import time
import os.path
import json
import requests

API_KEY = 'ailckcattnyvxxfu'
SERVER = 'nova.astrometry.net'
#SERVER = 'localhost:8080'

def solve(filename, session_key=None, api_key=API_KEY):
    if not session_key:
        print('Logging in with apikey')
        session_key = login(api_key)
    submission_id = submit_image(filename, session_key)
    submission_status_url = 'http://{}/status/{}'.format(SERVER, submission_id)
    print('See submission status at: {}'.format(submission_status_url))

    print('Waiting for solve...')
    while True:
        job_id = get_job_id(submission_id)
        if job_id:
            break
        else:
            time.sleep(2)
            print('.', end='', flush=True)

    while True:
        job_status = get_job_status(job_id)
        if job_status == 'solving':
            time.sleep(2)
            print('.', end='', flush=True)
        elif job_status == 'failure':
            print()
            print('Could not solve image!')
            return
        else:
            print()
            break

    calibration_result = get_calibration_results(job_id)
    return calibration_result, session_key


def get_job_id(submission_id):
    submissions_url = 'http://{}/api/submissions/{}'.format(SERVER, submission_id)
    response = requests.get(submissions_url).json()
    return response['jobs'][0] if response['jobs'] else None


def get_job_status(job_id):
    job_url = 'http://{}/api/jobs/{}'.format(SERVER, job_id)
    response = requests.get(job_url).json()
    return response['status']


def get_calibration_results(job_id):
    calibration_url = 'http://{}/api/jobs/{}/calibration/'.format(SERVER, job_id)
    calibration_response = requests.get(calibration_url).json()
    return calibration_response


def login(api_key):
    login_url = 'http://{}/api/login'.format(SERVER)
    request_data = {'request-json': json.dumps({'apikey': api_key})}
    response = requests.post(login_url, data=request_data)
    response_json = response.json()
    if response_json['status'] != 'success':
        raise RuntimeError('Could not log in!')
    session_key = response_json['session']
    return session_key


def submit_image(filename, session_key):
    arguments_json = json.dumps({
        'session': session_key,
        'allow_commercial_use': 'n'
        })
    _, filename_tail = os.path.split(filename)

    multipart_data = {
        'request-json' : (None, arguments_json, 'text/plain'),
        'file': (filename_tail, open(filename, 'rb'), 'application/octet-stream')
    }

    upload_url = 'http://{}/api/upload'.format(SERVER)
    response = requests.post(upload_url, files=multipart_data)
    if response.status_code != 200:
        raise RuntimeError('API responded with HTTP {}'.format(response.status_code))

    response_json = response.json()
    if response_json['status'] != 'success':
        raise RuntimeError('Could not process image: {}'.format(response_json))
    return response_json['subid']


if __name__ == '__main__':
    print(solve('cygnus.jpg')[0])
