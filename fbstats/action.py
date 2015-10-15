import re
from collections import namedtuple
from functools import partial


Command = namedtuple('Command', ['regex', 'action', 'signature'])


class Action():
	def __init__(self):
		self._commands = []


	def concat_args(self, args):
		if (len(args) == 0):
			raise Exception('no command')
			#default action?

		allargs = ''
		for i in range(0, len(args)):
			allargs += args[i].strip() + ' '
		return allargs


	def do(self, args):			
		if isinstance(args, list):
			args = self.concat_args(args)

		for command in self._commands:
			sig = command.signature
			match = command.regex.match(args)
			if match:
				if sig:
					kwargs = dict([(k,sig[k](v)) for (k,v) in match.groupdict().items() if v])	#typecast
				else:				
					kwargs = dict([(k,v) for (k,v) in match.groupdict().items() if v])

				if len(kwargs) > 0:		#if kwargs found, call only with kwargs
					return command.action(**kwargs)
 
				args = tuple(a for a in match.groups() if a not in match.groupdict().values())		#filter out dict values

				if not sig or len(args) == 0:
					return self.curry_call(command.action, args)
				else:
					targs = tuple([sig[i](a) for (a,i) in zip(args, range(0, len(sig)))])		#typecast
					targs += args[len(sig):]
					return self.curry_call(command.action, targs)
		print('syntax error')
						

	def curry_call(self, func, args):
		if len(args) > 0:
			return self.curry_call(partial(func, args[0]), args[1:])
		else:
			return func()
		

	def register(self, regex, action, signature=None):
		self._commands.append(Command(re.compile(regex), action, signature))


#todo: mix of args and kwargs
#assert: for args, signature is in tuple; for kwargs it is in a dictionary
