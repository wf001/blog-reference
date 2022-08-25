import logging
import inspect
import traceback
import json
from http import HTTPStatus
from flask import request, jsonify


class FormatterJSON(logging.Formatter):
    def format(self, record):
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        j = {
            'logLevel': record.levelname,
            'extra_data': record.__dict__.get('extra_data', {}),
            'aws_request_id': getattr(record, 'aws_request_id', '00000000-0000-0000-0000-000000000000'),
            'message': record.getMessage(),
            'module': record.module,
            'filename': record.filename,
            'funcName': record.funcName,
            'levelno': record.levelno,
            'lineno': record.lineno,
            'traceback': {},
            'timestamp': '%(asctime)s.%(msecs)dZ' % dict(asctime=record.asctime, msecs=record.msecs),
            'event': record.__dict__.get('event', {}),
        }
        if record.exc_info:
            exception_data = traceback.format_exc().splitlines()
            j['traceback'] = exception_data

        return json.dumps(j, ensure_ascii=False)


logger = logging.getLogger()
logger.setLevel('INFO')

formatter = FormatterJSON(
    '[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(levelno)s\t%(message)s\n',
    '%Y-%m-%dT%H:%M:%S'
)
# Replace the LambdaLoggerHandler formatter :
if len(logger.handlers) > 0:
    logger.handlers[0].setFormatter(formatter)


def _info(data):
    i = inspect.stack()[1]
    file_name = i.filename.split('/')[-1]
    lineno = str(i.lineno)
    func_name = i.function
    print('\nINFO #######',
          file_name+'('+lineno+')::'+func_name+"\n",
          data)


def catch_exception(f):

    def wrapped(*args, **kwargs):
        try:
            logger.info('', extra=dict({
                'extra_data': {
                    'METHOD': request.method,
                    'PATH': request.path
                }
            }
            ))
            return f(*args, **kwargs)

        except Exception as e:
            logging.exception(e)
            return jsonify({'error_message': str(e)}),\
                HTTPStatus.BAD_REQUEST
    wrapped.__name__ = f.__name__
    return wrapped
