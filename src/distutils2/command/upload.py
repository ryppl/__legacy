"""distutils.command.upload

Implements the Distutils 'upload' subcommand (upload package to PyPI)."""
import os
import socket
import platform
from urllib2 import urlopen, Request, HTTPError
from base64 import standard_b64encode
import urlparse
import cStringIO as StringIO
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from distutils2.errors import DistutilsOptionError
from distutils2.core import PyPIRCCommand
from distutils2.spawn import spawn
from distutils2 import log

class upload(PyPIRCCommand):

    description = "upload binary package to PyPI"

    user_options = PyPIRCCommand.user_options + [
        ('sign', 's',
         'sign files to upload using gpg'),
        ('identity=', 'i', 'GPG identity used to sign files'),
        ]

    boolean_options = PyPIRCCommand.boolean_options + ['sign']

    def initialize_options(self):
        PyPIRCCommand.initialize_options(self)
        self.username = ''
        self.password = ''
        self.show_response = 0
        self.sign = False
        self.identity = None

    def finalize_options(self):
        PyPIRCCommand.finalize_options(self)
        if self.identity and not self.sign:
            raise DistutilsOptionError(
                "Must use --sign for --identity to have meaning"
            )
        config = self._read_pypirc()
        if config != {}:
            self.username = config['username']
            self.password = config['password']
            self.repository = config['repository']
            self.realm = config['realm']

        # getting the password from the distribution
        # if previously set by the register command
        if not self.password and self.distribution.password:
            self.password = self.distribution.password

    def run(self):
        if not self.distribution.dist_files:
            raise DistutilsOptionError("No dist file created in earlier command")
        for command, pyversion, filename in self.distribution.dist_files:
            self.upload_file(command, pyversion, filename)

    def upload_file(self, command, pyversion, filename):
        # Makes sure the repository URL is compliant
        schema, netloc, url, params, query, fragments = \
            urlparse.urlparse(self.repository)
        if params or query or fragments:
            raise AssertionError("Incompatible url %s" % self.repository)

        if schema not in ('http', 'https'):
            raise AssertionError("unsupported schema " + schema)

        # Sign if requested
        if self.sign:
            gpg_args = ["gpg", "--detach-sign", "-a", filename]
            if self.identity:
                gpg_args[2:2] = ["--local-user", self.identity]
            spawn(gpg_args,
                  dry_run=self.dry_run)

        # Fill in the data - send all the meta-data in case we need to
        # register a new release
        content = open(filename,'rb').read()
        meta = self.distribution.metadata

        data = {
            # action
            ':action': 'file_upload',
            'protcol_version': '1',

            # identify release
            'name': meta['Name'],
            'version': meta['Version'],

            # file content
            'content': (os.path.basename(filename),content),
            'filetype': command,
            'pyversion': pyversion,
            'md5_digest': md5(content).hexdigest(),

            # additional meta-data
            # XXX Implement 1.1
            'metadata_version' : '1.0',
            'name': meta['Name'],
            'version': meta['Version'],
            'summary': meta['Summary'],
            'home_page': meta['Home-page'],
            'author': meta['Author'],
            'author_email': meta['Author-email'],
            'license': meta['License'],
            'description': meta['Description'],
            'keywords': meta['Keywords'],
            'platform': meta['Platform'],
            'classifiers': meta['Classifier'],
            'download_url': meta['Download-URL'],
            #'provides': meta['Provides'],
            #'requires': meta['Requires'],
            #'obsoletes': meta['Obsoletes'],
            }
        comment = ''
        if command == 'bdist_rpm':
            dist, version, id = platform.dist()
            if dist:
                comment = 'built for %s %s' % (dist, version)
        elif command == 'bdist_dumb':
            comment = 'built for %s' % platform.platform(terse=1)
        data['comment'] = comment

        if self.sign:
            data['gpg_signature'] = (os.path.basename(filename) + ".asc",
                                     open(filename+".asc").read())

        # set up the authentication
        auth = "Basic " + standard_b64encode(self.username + ":" +
                                             self.password)

        # Build up the MIME payload for the POST data
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
        sep_boundary = '\n--' + boundary
        end_boundary = sep_boundary + '--'
        body = StringIO.StringIO()
        for key, value in data.items():
            # handle multiple entries for the same name
            if not isinstance(value, list):
                value = [value]
            for value in value:
                if isinstance(value, tuple):
                    fn = ';filename="%s"' % value[0]
                    value = value[1]
                else:
                    fn = ""

                body.write(sep_boundary)
                body.write('\nContent-Disposition: form-data; name="%s"'%key)
                body.write(fn)
                body.write("\n\n")
                body.write(value)
                if value and value[-1] == '\r':
                    body.write('\n')  # write an extra newline (lurve Macs)
        body.write(end_boundary)
        body.write("\n")
        body = body.getvalue()

        self.announce("Submitting %s to %s" % (filename, self.repository), log.INFO)

        # build the Request
        headers = {'Content-type':
                        'multipart/form-data; boundary=%s' % boundary,
                   'Content-length': str(len(body)),
                   'Authorization': auth}

        request = Request(self.repository, data=body,
                          headers=headers)
        # send the data
        try:
            result = urlopen(request)
            status = result.getcode()
            reason = result.msg
        except socket.error, e:
            self.announce(str(e), log.ERROR)
            return
        except HTTPError, e:
            status = e.code
            reason = e.msg

        if status == 200:
            self.announce('Server response (%s): %s' % (status, reason),
                          log.INFO)
        else:
            self.announce('Upload failed (%s): %s' % (status, reason),
                          log.ERROR)
        if self.show_response:
            self.announce('-'*75, result.read(), '-'*75)
