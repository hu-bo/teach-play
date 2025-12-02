from auto_executor.core.playback.executor import Executor
import sys


def main():
    if len(sys.argv) < 2:
        print('Usage: play.py <recording.json>')
        return
    path = sys.argv[1]
    e = Executor()
    e.load(path)
    e.run()


if __name__ == '__main__':
    main()
