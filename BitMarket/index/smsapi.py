from django.contrib.auth.models import User
import requests
class Smsapi
    
    def __init__(self, username, password):
        """
        na razie jest tak, bo tak, a później bedzie bezpiczeniej... teraz ważne aby działało
        """
        u = username
        p = password
        url = '- https://ssl.smsapi.pl/sms.do'
        
    def sendConfirmationOfCommission(self, user = User()):
        User.
        
    def call(self, url, params=None):
        """
        Wysyła requesta z paramsami.
        """
        if params is None: params = {}
        params['key'] = self.apikey
        params = json.dumps(params)
        self.log('POST to %s%s.json: %s' % (ROOT, url, params))
        start = time.time()
        r = self.session.post('%s%s.json' % (ROOT, url), data=params, headers={'content-type': 'application/json', 'user-agent': 'Mandrill-Python/1.0.53'})
        try:
            remote_addr = r.raw._original_response.fp._sock.getpeername() # grab the remote_addr before grabbing the text since the socket will go away
        except:
            remote_addr = (None, None) #we use two private fields when getting the remote_addr, so be a little robust against errors

        response_body = r.text
        complete_time = time.time() - start
        self.log('Received %s in %.2fms: %s' % (r.status_code, complete_time * 1000, r.text))
        self.last_request = {'url': url, 'request_body': params, 'response_body': r.text, 'remote_addr': remote_addr, 'response': r, 'time': complete_time}

        result = json.loads(response_body)

        if r.status_code != requests.codes.ok:
            raise self.cast_error(result)
        return result