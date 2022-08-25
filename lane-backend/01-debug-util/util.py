import inspect


def _info(data):
    i = inspect.stack()[1]
    file_name = i.filename.split('/')[-1]
    lineno = str(i.lineno)
    func_name = i.function
    print('\nINFO #######',
          file_name+'('+lineno+')::'+func_name+"\n",
          data)
