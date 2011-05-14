import inspect
import optparse

def reflect_options(func, help={}, **overrides):
    spec = inspect.getargspec(func)

    f_args = spec.args
    f_kwargs = zip(f_args[::-1], ((spec.defaults or []))[::-1])[::-1]
    if f_kwargs:
        f_args = spec.args[:-len(f_kwargs)]
    
    usage = ['usage: %prog [options]']
    usage.extend(f_args)
    if spec.varargs:
        usage.append('[%s]...' % spec.varargs)
        
    parser = optparse.OptionParser(usage=' '.join(usage))
    
    used_shorts = set()
    for arg, default in f_kwargs:
        opts = ['--%s' % arg]
        
        # Find a short version
        def find_short(arg):
            for l in arg:
                for f in (str, str.swapcase):
                    short = f(l)
                    if short not in used_shorts:
                        return short
        try:
            short = find_short(arg)
            if short:
                used_shorts.add(short)
                opts.append('-%s' % short)
        except IndexError:
            pass

        # Handle defaults
        kwopts = dict(default=default, help=help.get(arg, ''))
        
        if isinstance(default, bool):
            if default is False:
                kwopts['action'] = 'store_true'
            else:
                default = None
        elif isinstance(default, (int, long, float, complex)):
            kwopts['type'] = type(default).__name__
        elif isinstance(default, (list, tuple)):
            kwopts['action'] = 'append'

        if default:
            if kwopts['help']: kwopts['help'] += ' '
            kwopts['help'] += '[default: %default]'
            
        # Per-arg overrides
        override = overrides.get(arg, {})
        opts = override.pop('opts', opts)
        kwopts.update(override)
            
        parser.add_option(*opts, **kwopts)

    (options, args) = parser.parse_args()
    
    if len(args) < len(f_args) or (
      not spec.varargs and len(args) > len(f_args)):
        import sys
        parser.print_help()
        sys.exit(1)

    return func(*args, **options.__dict__)


if __name__ == '__main__':
    import sys
    try:
        print reflect_options(eval(sys.argv.pop(1)))
    except IndexError:
        print 'try: optflection.py "lambda required, optional=1: (required, optional)"'
