# pokertools

A terminal app for practicing poker hand reading — deal a hand, reveal the board street by street, and see your hand strength, draws, and odds update live.

## Features

- Deals hole cards and a full community board from a shuffled deck
- Reveals the flop, turn, and river one street at a time
- Evaluates your best five-card hand (pair through straight flush, with set-vs-trips and made-straight naming)
- Detects live draws — flush, straight, gutshot, double gutshot, and backdoor draws — with out counts, hit chance, and odds against
- Remembers your chosen color theme between sessions

## Controls

| Key      | Action                   |
| -------- | ------------------------ |
| `d`      | Deal a fresh hand        |
| `n`      | Reveal the next street   |
| `s`      | Show / hide draw details |
| `o`      | Open the odds exercise   |
| `r`      | Return to the README     |
| `escape` | Clear focus              |
| `q`      | Quit                     |

## Getting started

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```sh
uv run src/main.py
```

## Tech stack

Built with [Textual](https://textual.textualize.io/) for the terminal UI, with preferences persisted via `platformdirs`.
