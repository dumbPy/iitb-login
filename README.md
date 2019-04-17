# IITB LOGIN

This package consists a login script for headless login to `internet.iitb.ac.in` on any of the iitb servers.  
It uses ssh key to encrypt your credentials safely for hastle-free login.

## Install
`pip install iitb-login` should install the script. 

Works strictly on python 3.x versions. Does not support python 2.7 or older

If you are on older OS like ubuntu 16.04 or older and not using Anaconda3 installation already, It has default python to python 2.7, thus first install pip3 with `sudo apt install python3-pip` then this script with `pip3 install iitb-login`

### Usage
#### First time using ssh key
```
$ iitb login      # to login. Enter username and password when prompted
# Enter username: username
# enter password: 
# Logged In As :  username
# Your IP:        10.119.xxx.xxx

# Encrypting with key:   /home/username/.ssh/<ssh-key-name>
# This Script uses your ssh key to encrypt credentials
# Save credentials:  [y/N]: y
# Credentials written to file: ~/.ssh/iitb_login_creds and can only be 
# decrypted with your ssh key
```

#### Next time onwards
```
$ iitb login
# Logged In as username
# Your IP:     10.119.xxx.xxx
```

#### Other Options
```
$ iitb logout # to logout
$ iitb status # to check status of login
$ iitb        # to check status of login (default argument is status)
$ iitb reset  # to delete the saved encrypted credentials
```

#### In case you use multiple ssh keys
You can select which key to use to encrypt the credentials. 
```
$ iitb login
# Enter username: username
# Enter password
# Logged In as username
# Your IP:     10.119.xxx.xxx
# Keys available:
# [0]   /home/username/.ssh/id_rsa
# [1]   .ssh/google/google_compute_engine
# Select Key Index: 0
# This Script uses your ssh key to encrypt credentials
# Save credentials:  [y/N]: y
# Credentials written to file: ~/.ssh/iitb_login_creds and can only be 
# decrypted with your ssh key
```


### How It Works
#### Scrapy Spider

Scrapy Spider is used to load `https://internet.iitb.ac.in`, parse the page, check passed argument parsed by `ArgumentParser` and filling the form for subsiquent `POST` request for login and logout. Methods `get_username(response)` is used to parse logged in user's username and `get_ip(response)` to parse machine's ip address.

#### Paramiko
`paramiko.Agent()` connects to exposed or forwarded `ssh-agent`'s api on the machine and use it's keys to sign a random string. The signature of the string changes with each ssh key. Hence, credentials encrypted with one key can only be decrypted by the same key.  
These encrypted keys can now be saved in a pickle file at `~/.ssh/iitb_login_creds` without the risk of exposing the credentials.

The keys from `paramiko.Agent().get_keys()` have a `sign_ssh_data()` method that is used to get the symetric key used for encryptng the credentials. As the signature returned is dependent of the private key being used for signing, the credentials are safe in a pickle dump and only be decrypted using the same key.

### Version History
`v 0.1.2` First release. wrong ip address parsing  
`v 0.1.3` ip parsing patched  
`v 0.1.4` Allows choosing ssh key in case of multiple keys  
`v 0.2.1` First Stable Release. README updated, setup.py url fixed.

## Future Changes
In case the script becomes outdated and needs an update, feel free to make a pull request, or create an issue on github.
