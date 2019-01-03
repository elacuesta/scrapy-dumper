import logging
import string
import os
from datetime import datetime
from contextlib import suppress

import scrapy


def safe_filename(filename):
    _filename = str(filename).replace('/', '|')
    whitelist_characters = string.ascii_letters + string.digits + '|'
    return ''.join([c for c in _filename if c in whitelist_characters])


REQUESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../_requests')
RESPONSES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../_responses')


def dump(message, directory, filename, extension, body, headers, url, method, status):
    filepath = f'{directory}/{filename}.{extension}'
    with open(filepath, 'w') as file:
        if extension in ('html', 'xml', 'text'):
            headers = [
                '{}: {}'.format(key.decode('utf8'), value[0].decode('utf8'))
                for key, value in headers.items()
            ]
            data = [
                '<!--',
                message,
                f'URL: {url}',
                f'Method: {method}',
                f'Status: {status}',
                '-->',
                '<!-- Headers -->',
                '<!--',
                *headers,
                '-->',
                '<!-- Body -->',
            ]
            print(*data, file=file, sep='\n')
        print(body, file=file)


class DumperExtension:
    """
    Dump requests and responses to disk, for debugging purposes.
    """

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('DEBUG_DUMP_REQUESTS_RESPONSES'):
            raise scrapy.exceptions.NotConfigured
        ext = cls()
        crawler.signals.connect(ext.request_scheduled, signal=scrapy.signals.request_scheduled)
        crawler.signals.connect(ext.response_received, signal=scrapy.signals.response_received)
        with suppress(FileExistsError):
            os.mkdir(REQUESTS_DIR)
        with suppress(FileExistsError):
            os.mkdir(RESPONSES_DIR)
        ext.logger = logging.getLogger(__name__)
        return ext

    def request_scheduled(self, request, spider):
        try:
            filename = '{now}_{url}_{method}'.format(
                now=datetime.now().isoformat(),
                url=safe_filename(request.url),
                method=request.method,
            )
            content_type = request.headers.get('Content-Type', b'application/text').decode('utf8')
            extension = content_type.split(';')[0].split('/')[-1]
            body = request.body if request.body else b'(Empty body)'
            dump(
                message='REQUEST',
                directory=REQUESTS_DIR,
                filename=filename,
                extension=extension,
                body=body.decode('utf8'),
                headers=request.headers,
                url=request.url,
                method=request.method,
                status='N/A',
            )
        except Exception as ex:
            self.logger.debug('Could not dump request: %s. Exception: %s', str(request), str(ex))

    def response_received(self, response, request, spider):
        try:
            filename = '{now}_{url}_{method}_{status}'.format(
                now=datetime.now().isoformat(),
                url=safe_filename(response.url),
                method=request.method,
                status=response.status,
            )
            content_type = response.headers.get('Content-Type', b'application/text').decode('utf8')
            extension = content_type.split(';')[0].split('/')[-1]
            dump(
                message='RESPONSE',
                directory=RESPONSES_DIR,
                filename=filename,
                extension=extension,
                body=response.text,
                headers=response.headers,
                url=response.url,
                method=request.method,
                status=response.status,
            )
        except Exception as ex:
            self.logger.debug('Could not dump request: %s. Exception: %s', str(response), str(ex))
