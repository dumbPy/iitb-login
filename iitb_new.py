import scrapy
from scrapy.crawler import CrawlerProcess
import paramiko
import click, time, sys
from argparse import ArgumentParser
from cryptography import fernet
import logging, os, getpass, pickle

class IITB_Spider(scrapy.Spider):
    name = 'iitb_crawler'
    
    def __init__(self, command):
        self.command = command

        logger=logging.getLogger('scrapy')
        logger.propogate=False
        super().__init__()

    def start_requests(self):
        url = 'https://internet.iitb.ac.in'
        yield scrapy.Request(url, callback=self.parse_page)
    
    def parse_page(self, response):
        if self.command=='logout':
            return self.logout(response)
        elif self.command=='login':
            return self.login(response)
        elif self.command=='status':
            response.meta['from'] = 'status'
            return self.confirm(response)
        else: print('No valid argument Passed!!!')

    def logout(self, response):
        if self.is_logged_in(response):
            # print('In Logout Handler, sending logout request!!!')
            request = scrapy.FormRequest.from_response(response, formname='auth', 
                                                   formdata={'ip':self.get_ip(response),
                                                             'etype':'pg', 
                                                             'button':'Logout', 
                                                             'etype':'pg'}, 
                                                   callback=self.confirm)
            request.meta['from']='logout'
            yield request
        else: print('Seems to be logged out already!!')
            
    def login(self, response):
        if self.is_logged_in(response): 
            print(f'Already Logged In as:    {self.get_username(response)}')
            print(f'Your IP:                 {self.get_ip(response)}')
        else:
            # print('Logging In..')
            creds = read_creds()
            username = creds['username']
            password = creds['password']
            request =  scrapy.FormRequest.from_response(response, formname='auth', 
                                                   formdata={'uname':username, 
                                                             'passwd':password, 
                                                             'button':'Login'}, 
                                                   callback=self.confirm)
            request.meta['from']='login'
            request.meta['creds']=creds
            yield request
            
    def confirm(self, response):
        # print('reached confirm')
        url = 'https://internet.iitb.ac.in'
        request = response.follow(url=url, callback=self.confirm_response, dont_filter=True)
        try: request.meta['creds']=response.meta['creds']
        except: pass
        request.meta['from']=response.meta['from']
        yield request
        
    def confirm_response(self, response):
        # print('reached confirm response')
        if response.meta['from']=='login' and 'logout' in response.url:
            print(f'Logged In as {self.get_username(response)}')
            print(f'Your IP:     {self.get_ip(response)}')
            crypto = get_crypto()
            if crypto is not None: write_creds(crypto, response.meta['creds'])

        elif response.meta['from']=='logout' and not 'logout' in response.url:
            print('Logged Out')
        elif response.meta['from'] == 'status':
            if 'logout' in response.url: 
                print(f'Logged in as {self.get_username(response)}')
                print(f'Your IP:     {self.get_ip(response)}')
            else: print('Not Logged In to internet.iitb.ac.in')
        else:
            print(response.url)
            print(f'{response.meta["from"]} Failed !!!!!')
    
    def is_logged_in(self, response):
        if 'logout' in response.url: return True
        else: return False

        
    def get_username(self,response):
        return response.xpath('//div[@class="scrolling"]//td[1]/center/text()')[0].extract().strip()
    def get_ip(self,response):
        return response.xpath('//div[@class="scrolling"]//td[2]/center/text()')[0].extract().strip()


def get_crypto()-> fernet.Fernet:
    """
    Method that returns Fernet class,
    Initialized with signature of a random text below, signed by your ssh key
    """
    # Agent that connects to SSH Agent (including forwarded agents)
    agent=paramiko.Agent()
    # If no ssh key in agent is found, return None
    try: key = agent.get_keys()[0]
    except: return
    # Use 1st ssh key in your agent to sign a random text.
    password = key.sign_ssh_data('Random Text Whose SSH Key Signature Is Used As Key')
    encode = fernet.base64.b64encode # base64 encoder
    # get base64 encoded 32 length part of signature
    password = encode(encode(password)[:32])
    # Init a Fernet with above password
    return fernet.Fernet(password)

def encrypt(crypto:fernet.Fernet, string:str)-> bytes:
    """Args
    -----
    crypto:     Fernet object initialized with ssh key based signature
                check `get_crypto()` method for initialization
    string:     String to encrypto with the Fernet object passed
                the string is converted to bytes and then encrypted
    """
    return crypto.encrypt(str.encode(string))

def decrypt(crypto:fernet.Fernet, encrypted:bytes)-> str:
    """
    Args
    -----
    crypto:     Fernet object initialized with ssh key based signature
                check `get_crypto()` method for initialization
    encrypted:  Encrypted bytes string to be decoded with Fernet
    """
    return crypto.decrypt(encrypted).decode()

def read_creds()->dict:
    
    path = os.path.expanduser('~/.ssh/iitb_login_creds')
    crypto = get_crypto()
    if crypto is None or not os.path.exists(path):
        username = input('Enter username: ')
        password = getpass.getpass('Enter password')
        return {'username':username,
                'password':password}

    else:
        with open(path, 'rb') as f:
            creds=pickle.load(f)
            assert(len(creds)==2),"credentials read from ~/.ssh/iitb_login_creds are faulty. \
            Please delete the file and try storing new credentials"
            
        return {'username': decrypt(crypto, creds['username']),
                'password': decrypt(crypto, creds['password'])}
def write_creds(crypto:fernet.Fernet, creds:dict)->None:
    
    path = os.path.expanduser('~/.ssh/iitb_login_creds')
    if os.path.exists(path): return

    print('This Script uses your ssh key to encrypt credentials')
    if not click.confirm('Save credentials: '): return
    
    creds['username'] = encrypt(crypto, creds['username'])
    creds['password'] = encrypt(crypto, creds['password'])
    with open(path, 'wb') as f:
        pickle.dump(creds, f)
        
    print('Credentials written to file: ~/.ssh/iitb_login_creds and only be decrypted with your ssh key')


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Script for headless login and logout on all IITB servers')
    parser.add_argument('command', nargs='?', default='status', 
            choices=['login', 'logout', 'status'], 
            help='you can either pass login, logout or status')

    args = parser.parse_args()
    crypto = get_crypto()

    crawler = CrawlerProcess(settings={'LOG_ENABLED': True, 'LOG_LEVEL':'ERROR'})
    crawler.crawl(IITB_Spider, command=args.command)
    crawler.start()
    