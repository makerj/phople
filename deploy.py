import os
import subprocess
from argparse import ArgumentParser
from os.path import abspath as absp, join as joinp, dirname as dirn, basename as basen

site_path = dirn(absp(__file__))
site_name = basen(site_path)
log_path = joinp(site_path, 'log')
args = None  # commandline arguments

vhost = """
<VirtualHost {listen}>
    ServerName {server_name}
    ServerAlias {server_alias}
    ServerAdmin {server_admin}

    DocumentRoot {site_path}

    {aliases}

    WSGIScriptAlias / {site_path}/{site_name}/wsgi.py
    WSGIDaemonProcess {server_alias} python-path={site_path}:{python_path} lang='ko_KR.UTF-8' locale='ko_KR.UTF-8' {processes} {threads} display-name=%{{GROUP}}
    WSGIProcessGroup {server_alias}
    WSGIPassAuthorization On

    <Directory {site_path}/{site_name}>
    <Files wsgi.py>
    Require all granted
    </Files>
    </Directory>

    ErrorLog {log_path}/error.log
    CustomLog {log_path}/custom.log combined
</VirtualHost>
"""


def find_python_dist_path():
    import django
    import re
    django_path = dirn(absp(re.search(r'.*from \'(?P<path>.*)\'.*', str(django)).group('path')))
    dist_path = absp(dirn(django_path))
    return dist_path


def dinput(prompt, default):
    v = input(prompt)
    return v if len(v) else default


def dfinput(prompt, key, default):
    value = input(prompt)
    return '{0}={1}'.format(key, value) if len(value) else default


def gen_aliases():
    aliases = []
    aliasform = 'Alias {0} {1}'
    while True:
        v = input('Enter aliases for static file hosting. e.g. URL>PATH [default: EMPTY]:')
        if len(v):
            url, path = v.split('>')
            aliases.append(aliasform.format(url, path))
        else:
            break

    return '\n    '.join(aliases)


def format_auto():
    global vhost
    vhost = vhost.format(listen='*:80 *:443', server_name='api.{0}.us'.format(site_name), server_alias=site_name,
                         server_admin='webmaster@{0}.us'.format(site_name), site_path=site_path, aliases='',
                         site_name=site_name, python_path=find_python_dist_path(), processes='', threads='',
                         log_path=log_path)


def set_logpath():
    global log_path
    log_path = dinput('Enter log_path [default: SITE_PATH/log/]: ', log_path)
    return log_path


def format_custom():
    global vhost
    vhost = vhost.format(
        listen=dinput('Enter listening host:port pair [default: *:80 *:443]: ', '*:80 *:443'),
        server_name=dinput('Enter server name [default: www.SITE_NAME.com]: ', 'www.{0}.com'.format(site_name)),
        server_alias=dinput('Enter server alias [default: SITE_NAME]: ', site_name),
        server_admin=dinput('Enter server admin email address [default: webmaster@SITE_NAME.com]: ',
                            'webmaster@{0}.com'.format(site_name)),
        site_path=site_path,
        aliases=gen_aliases(),
        site_name=site_name,
        python_path=find_python_dist_path(),
        processes=dfinput('Enter server process count [default: AUTO]: ', 'processes', ''),
        threads=dfinput('Enter server thread count [default: AUTO]: ', 'threads', ''),
        log_path=set_logpath()
    )


def isroot():
    return os.getuid() == 0


def install_required_modules():
    try:
        with open(joinp(site_path, 'required_module')) as f:
            for line in filter(lambda l: not l.replace('\n', '').startswith('#'), f.readlines()):
                subprocess.call(line.split())
    except FileNotFoundError:
        print("file 'required_module' not exists. pass this step")

    if args.mode == 'install_module':
        quit()


def save_vhost():
    with open('/etc/apache2/sites-available/{0}.conf'.format(site_name), 'w') as f:
        f.write(vhost)


def generate_vhost():
    if args.mode == 'auto':
        format_auto()
    elif args.mode == 'custom':
        format_custom()
    else:
        print('wrong switch. please use correct switch')
        quit()


if __name__ == '__main__':
    if not isroot():
        raise PermissionError('this program must run with superuser privilege. perhaps forgot sudo?')
    ap = ArgumentParser('makers django application automatic deployment script')
    ap.add_argument('mode', choices=['auto', 'custom', 'install_module'], help='select script mode')
    args = ap.parse_args()

    print('Installing required modules...')
    install_required_modules()

    print('generating virtual host file...')
    generate_vhost()

    print('generated virtual host file...')
    print(vhost)

    print('preparing log directory...')
    os.makedirs(log_path, exist_ok=True)

    print('save virtual host file and enabling...')
    save_vhost()
    subprocess.call(['a2ensite', site_name + '.conf'])

    print('reloading apache2...')
    subprocess.call('service apache2 start'.split())
    subprocess.call('service apache2 reload'.split())

    print('done!')
