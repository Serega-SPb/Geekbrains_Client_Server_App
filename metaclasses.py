import types
import dis


def disassemble(clsdict, black_list):
    funcs = [a for a in clsdict.values() if isinstance(a, types.FunctionType)]
    instructions = [list(dis.get_instructions(f)) for f in funcs]
    for instr in instructions:
        socket_step_to_call = 0  # кол-во инструкций начиная с 'LOAD_GLOBAL' инструкции для socket
        for i in instr:

            if socket_step_to_call > 0:
                socket_step_to_call += 1
                if i.opname.startswith('CALL_FUNCTION'):
                    if socket_step_to_call <= 2:
                        raise TypeError('Incorrect socket usage')  # вызов socket без параметров
                    else:
                        socket_step_to_call = 0  # вызов socket с параметрами

            if i.opname in ['LOAD_GLOBAL', 'LOAD_METHOD']:
                if i.argval == 'socket':
                    socket_step_to_call += 1
                if i.argval in black_list:
                    raise TypeError('Call method of socket from black list')
    pass


class Singleton(type):

    def __init__(cls, *args, **kwargs):
        super(Singleton, cls).__init__(*args, **kwargs)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class ServerVerifier(type):
    methods_black_list = ['connect']

    def __init__(cls, clsname, bases, clsdict):
        disassemble(clsdict, cls.methods_black_list)
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    methods_black_list = ['accept', 'listen']

    def __init__(cls, clsname, bases, clsdict):
        disassemble(clsdict, cls.methods_black_list)
        super().__init__(clsname, bases, clsdict)
