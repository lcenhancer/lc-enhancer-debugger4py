if __name__ == '__main__':
    import sys
    from src.debugger4py import Debugger4py
    args_len = len(sys.argv)
    if args_len > 0:
        Debugger4py.__debugger_main__(sys.argv[-1])
