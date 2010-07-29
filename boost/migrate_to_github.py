# Copyright David Abrahams 2010. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
import re, os, sys, optparse, urlparse, tempfile, shutil
from subprocess import check_call
from github2.client import Github

submodule_header_pat=re.compile(r'\[\s*submodule\s+"(.*)"\s*\]\s*')
attrib_pat=re.compile(r'\s*(\S+)\s*=\s*(.*)')

def collect_submodules( gitmodules_file ):
    """
    >>> from StringIO import *
    >>> test_file = StringIO('''
    ... [submodule "accumulators"]
    ...	path = src/accumulators
    ...	url = git://gitorious.org/boost/accumulators.git
    ... [submodule "algorithm"]
    ...	path = src/algorithm
    ...	url = git://gitorious.org/boost/algorithm.git
    ... ''')

    >>> collect_submodules( test_file ) == {
    ...     'accumulators' : { 'path':'src/accumulators', 'url':'git://gitorious.org/boost/accumulators.git' },
    ...     'algorithm' : { 'path':'src/algorithm', 'url':'git://gitorious.org/boost/algorithm.git' } }
    True
    """
    submodules = {}
    last_submodule = None
    for line in gitmodules_file:
        text = line.strip()
        m = submodule_header_pat.match(text)
        if m:
            last_submodule = m.group(1)
            submodules[last_submodule] = {}
        else:
            m = attrib_pat.match(text)
            if m:
                submodules[last_submodule][m.group(1)] = m.group(2)

    return submodules

def mirror_repo( src_url, dst_url ):
    old_wd = os.getcwd()
    dir = tempfile.mkdtemp()
    try:
        os.chdir(dir)
        print 'in', dir
        check_call('git clone --bare'.split() + [src_url, 'repo'])
        os.chdir('repo')
        check_call('git push -v --mirror'.split() + [dst_url])
    finally:
        os.chdir(old_wd)
        shutil.rmtree(dir, ignore_errors=True)

def rdrop(s, suf):
    if s.endswith(suf):
        return s[:-len(suf)]
    return s
            
if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--test', dest='test', help='run doctests', default=False, action='store_true')
    parser.add_option('-u', '--user', dest='user', help='Github user name', default='boost-lib')
    parser.add_option('-t', '--token', dest='token', help='Github API token')
    
    (opts,args) = parser.parse_args()

    if opts.test:
        import doctest
        doctest.testmod()

    if len(args) > 0:
        gitorious_master_path = args[0]
        submodules = list(
            collect_submodules(open( os.path.join(gitorious_master_path, '.gitmodules') )).items()
            )
        # For whatever reason, this makes them come out alphabetically in GitHub's index
        submodules.sort(reverse=True)

        if opts.token and opts.user:
            gh = Github(username=opts.user, api_token=opts.token)
        else:
            gh = Github()
        
        for x,attrs in submodules.items():
            url_path = urlparse.urlparse(attrs['url'])[2]
            name = rdrop(url_path.split('/')[-1], '.git')
            print '**',name
            new_path = 'boost-cpp/'+name
            new_repo = gh.repos.create(
                name, 'Boost.org %s module' % name, 'http://boost.org/libs/'+name)
            print new_repo
            mirror_repo(attrs['url'], 'git@github.com:'+new_path+'.git')
