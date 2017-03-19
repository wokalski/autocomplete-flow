#!/usr/bin/env python
# coding: utf-8

from .base import Base

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = 'flow'
        self.mark = '[flow]'
        self.filetypes = ['javascript']
        self.min_pattern_length = 2
        self.rank = 10000
        self.input_pattern = '((?:\.|(?:,|:|->)\s+)\w*|\()'
        self.__completer = Completer(vim)

    def get_complete_position(self, context):
        return self.__completer.determineCompletionPosition(context)

    def gather_candidates(self, context):
        return self.__completer.find_candidates(
            context
        )

class Completer(object):
    def __init__(self, vim):
        import re
        self.__vim = vim
        self.__completion_pattern = re.compile('\w*$')

    def get_flowbin(self):
        return self.__vim.vars['autocomplete_flow#flowbin']

    def determineCompletionPosition(self, context):
        result = self.__completion_pattern.search(context['input'])

        if result is None:
            return self.__vim.current.window.cursor.col

        return result.start()

    def abbreviateIfNeeded(self, text):
        return (text[:47] + '...') if len(text) > 50 else text

    def buildCompletionWord(self, json):

        # If not a function
        if not json['func_details']:
            return json['name']
            
        # If not using neosnippet
        if not self.__vim.vars['neosnippet#enable_completed_snippet']:
            return json['name'] + '('

        def buildArgumentList(arg):
            index, paramDesc = arg
            return '<`' + str(index) + ':' + paramDesc['name'] + '`>'

        params = map(buildArgumentList, enumerate(json['func_details']['params']))
        return json['name'] + '(' + ', '.join(params) + ')'

    def find_candidates(self, context):
        from subprocess import Popen, PIPE 
        import json

        line = str(self.__vim.current.window.cursor[0])
        column = str(self.__vim.current.window.cursor[1] + 1)
        command = [self.get_flowbin(), 'autocomplete', '--json', line, column]
        
        buf = '\n'.join(self.__vim.current.buffer[:])

        try:
            process = Popen(command, stdout=PIPE, stdin=PIPE)
            command_results = process.communicate(input=str.encode(buf))[0]

            if process.returncode != 0:
                return []

            results = json.loads(command_results.decode('utf-8'))

            return [{
                'word': self.buildCompletionWord(x),
                'abbr': self.abbreviateIfNeeded(x['name']),
                'info': x['type'],
                'kind': self.abbreviateIfNeeded(x['type'])} for x in results['result']]
        except FileNotFoundError:
            pass
