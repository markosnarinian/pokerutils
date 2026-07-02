import argparse

from app import PokertoolsApp


def is_dev_mode_active():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()
    return args.dev


def main():
    app = PokertoolsApp(dev_mode=is_dev_mode_active())
    app.run()


if __name__ == "__main__":
    main()
