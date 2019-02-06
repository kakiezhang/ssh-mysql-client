HOLE_COMMAND = 'ssh -fNg -L {local_port}:{aim_host}:{aim_port} {proxy_user}@{proxy_host} -P {proxy_port}'

LOCAL_CLI_COMMAND = 'mysql -h127.0.0.1 -u"{aim_user}" -p"{aim_pwd}" -P{local_port} -A'
LOCAL_DUMP_COMMAND = 'mysqldump -h127.0.0.1 -u"{aim_user}" -p"{aim_pwd}" -P{local_port} {extra_options}'

QUESTIONS = [
    {
        'col': 'aim_host',
        'desc': 'Please fill in the MySQL host:',
    },
    {
        'col': 'aim_port',
        'desc': 'Please fill in the MySQL port[default 3306]:',
        'default': 3306,
    },
    {
        'col': 'aim_user',
        'desc': 'Please fill in the MySQL username:',
    },
    {
        'col': 'aim_pwd',
        'desc': 'Please fill in the MySQL password:',
        'empty_allowed': True,
    },
    {
        'col': 'proxy_host',
        'desc': 'Please fill in the proxy host:',
    },
    {
        'col': 'proxy_port',
        'desc': 'Please fill in the proxy port[default 22]:',
        'default': 22,
    },
    {
        'col': 'proxy_user',
        'desc': 'Please fill in the proxy username:',
    },
    {
        'col': 'proxy_pwd',
        'desc': 'Please fill in the proxy password:',
        'empty_allowed': True,
    },
]
