from warnings import warn

def condition_warning(condition: str):
    warn(f'Found invalid condition \"{condition}\". Ignoring it.', RuntimeWarning)

def not_yet_implemented_warning(to_be_implemented: str):
    warn(f'{to_be_implemented} not yet implemented.', RuntimeWarning)