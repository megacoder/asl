#!/usr/bin/python
# vim: noet sw=4 ts=4

import	sys
import	os
import	datetime
import	traceback
import	re

try:
	from	version		import	Version
except:
	Version = '0.0.0rc0'

class	AdminServerLog( object ):

	STD_FIELDS = 12
	UNLIMITED  = 999
	CLAMPS     = [
		UNLIMITED,
		11,
		33,
		31,
		25,
		31,
		25,
	] + [ UNLIMITED ] * (STD_FIELDS - 7 )

	def	__init__( self, debug = 0 ):
		self.debug   = debug
		self.lines   = []
		self.widths  = dict()
		# Final field may be continued to next line and thus not
		# have a terminating '>'
		self.re      = re.compile( r'\s*<([^>]*)' )
		#
		self.ts_fmts = dict({
			'utc'   : r'%Y-%m-%dT%H:%M:%S.%f',
			'zoned' : r'%b %d, %Y %I:%M:%S %p',
		})
		self.ts_fmt = self.ts_fmts['utc']
		return

	def	_timestamp( self, s ):
		ts       = None
		if s[10] == 'T':
			spelling    = s[:-5]
			self.ts_fmt = self.ts_fmts['utc']
		else:
			tokens      = s.split()
			spelling    = ' '.join( tokens[:-1] )
			self.ts_fmt = self.ts_fmts['zoned']
		# Try the format that worked last time
		if self.ts_fmt:
			try:
				ts = datetime.datetime.strptime( spelling, self.ts_fmt )
			except:
				ts          = None
				self.ts_fmt = None
		# No format recognition so far, try them
		# all
		if not ts:
			for key in self.ts_fmts:
				self.ts_fmt = self.ts_fmts[key]
				try:
					ts = datetime.datetime.strptime( spelling, self.ts_fmt )
					break
				except Exception, e:
					ts          = None
					self.ts_fmt = None
		if not ts:
			print >>sys.stderr, 'Timestmap representation: {0}'.format( s )
			print >>sys.stderr, 'Chosen strptime:          {0}'.format(
				self.ts_fmt
			)
			print >>sys.stderr, 'Available strptime formats:'
			for key in self.ts_fmts:
				print >>sys.stderr, '  {0:>7} : "{1}"'.format(
					key,
					self.ts_fmts[key]
				)
			raise ValueError
		return ts

	def	clip( self, s, width = 30, ellipsis = '...' ):
		Ls = len( s )
		if Ls <= width: return s
		Le = len( ellipsis )
		keep = max(
			int( (width - Le) / 2 ),
			1
		)
		retval = '{0}{1}{2}'.format(
			s[:keep],
			ellipsis,
			s[-keep:],
		)
		return retval

	def	do_file( self, f = sys.stdin ):
		if self.debug:
			print 'do_file()'
		lineno = 0
		ts     = datetime.datetime.now()
		tokens = None
		extras = []
		for line in f:
			lineno += 1
			if self.debug > 1:
				print '{0:6d}\t{1}'.format( lineno, line )
			# Online lines beginning with '####' are interesting
			if line.startswith( '####' ):
				# Dump queued line, if any
				if tokens:
					self.lines.append(
						[ ts, tokens, extras ]
					)
					ts     = datetime.datetime.now()
					tokens = None
					extras = []
				tokens = self.re.findall(
					line.replace( '<<', '<' ).replace( '>>', '>' ).strip() +
					'>'
				)
				if len(tokens) == 0: continue
				# Non-blank line, interpret the tokens.  First one is
				# alwyas the timestamp.
				ts = self._timestamp( tokens[0] )
				if not ts:
					print >>sys.stderr, 'Timestamp not understood: {0}'.format(
						tokens[0]
					)
					ts = datetime.datetime.now()
				for i,t in enumerate( tokens[:AdminServerLog.STD_FIELDS] ):
					tokens[i] = self.clip(
						tokens[i],
						AdminServerLog.CLAMPS[ i ]
					)
				for i,f in enumerate( tokens[:AdminServerLog.STD_FIELDS] ):
					self.widths[ i ] = max(
						self.widths.get( i, 0 ),
						len( tokens[ i ] )
					)
				extra = ' '.join( tokens[AdminServerLog.STD_FIELDS:] )
				if len(extra):
					extras.append( extra )
				tokens = tokens[:AdminServerLog.STD_FIELDS]
			else:
				extra = line.rstrip()
				if len(extra) > 0 and extra[-1] == '>':
					extra = extra[:-1]
				if len(extra) > 0:
					extras.append( extra )
		if tokens:
			self.lines.append(
				[
					ts,
					tokens[:AdminServerLog.STD_FIELDS],
					extras + tokens[AdminServerLog.STD_FIELDS:]
				]
			)
		return

	def	process( self, name ):
		if self.debug:
			print 'process( {0} )'.format( name )
		if not os.path.exists( name ):
			print >>sys.stderr, 'No such file: {0}'.format( name )
			raise ValueError
		if os.path.isfile( name ):
			lineno = 0
			try:
				with open( name ) as f:
					lineno += 1
					if self.debug:
						print 'File opened: {0}'.format( name )
					self.do_file( f )
			except Exception, e:
				print >>sys.stderr, 'Failure on line {0}'.format( lineno )
				print >>sys.stderr, 'Could not process file "{0}" for some reason.'.format( name )
				print >>sys.stderr, e
				traceback.print_exc()
				raise e
		elif os.path.isdir( name ):
			try:
				for entry in sorted( os.listdir( name ) ):
					self.process(
						os.path.join(
							name,
							entry
						)
					)
			except Exception, e:
				print >>sys.stderr, 'Could not read directory "{0}", so there!'.format( name )
				traceback.print_exc()
				raise e
		else:
			pass
		return

	def	report( self, out = sys.stdout ):
		fmts = map(
			'{{0:<{0}.{0}s}}'.format,
			[ self.widths[i] for i in self.widths ]
		)
		N = len( fmts[:AdminServerLog.STD_FIELDS] )
		gutter = '  '
		indent = gutter.join([
			fmts[i].format('') for i in range( N - 1 )
		]) + gutter
		for ts,fields,extras in sorted(
			self.lines,
			key = lambda t : t[0]
		):
			line = gutter.join([
				fmts[i].format(fields[i]) for i in range( N )
			])
			print >>out, '{0}'.format( line.rstrip() )
			for extra in extras:
				print >>out, '{0}{1}'.format(
					indent,
					extra.rstrip()
				)
		return

def	main():
	import	optparse
	p = optparse.OptionParser(
		version = Version,
		description = 'Try to display AdminServer.log files in a human way.'
	)
	p.add_option(
		'-D',
		'--debug',
		dest   = 'debug',
		action = 'count',
		help   = 'enables debug output (up to a point).'
	)
	p.add_option(
		'-o',
		'--out',
		dest = 'ofile',
		metavar = 'FILE',
		default = None,
		help = 'write output to here; defaults to stdout.'
	)
	(opts,args) = p.parse_args()
	if opts.ofile:
		f = open( opts.ofile, 'w+' )
	else:
		f = sys.stdout
	asl = AdminServerLog( debug = opts.debug )
	if len( args ) == 0:
		asl.do_file()
	else:
		for arg in sorted( args ):
			asl.process( arg )
	asl.report( f )
	exit( 0 )

if __name__ == '__main__':
	main()
