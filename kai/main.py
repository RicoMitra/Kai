"""Kai: dynamic island desktop Windows tanpa mode suara.

  python main.py --island --demo  pratinjau island tanpa mikrofon atau model
  python main.py --island         Kai tanpa mode suara
  python main.py                  Kai tanpa mode suara
  python main.py --text "next"   uji perintah tanpa mikrofon
  python main.py --text "puter tulus" --dry   hanya tampilkan hasil pemahaman, tidak dijalankan
  python main.py --login         login Spotify sekali saja
"""
import argparse

import actions
import events
from events import emit
from intents import parse


def console(ev):
    print(f"[{ev.kind}] {ev.text}")


def handle_text(text, dry=False):
    intent = parse(text)
    emit("intent", f"{intent.name} {intent.args}")
    if dry:
        return
    emit("result", actions.run(intent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", help="uji perintah dari teks, tanpa mikrofon")
    ap.add_argument("--dry", action="store_true", help="hanya parse, jangan jalankan")
    ap.add_argument("--login", action="store_true", help="login Spotify")
    ap.add_argument("--island", action="store_true", help="tampilkan island tanpa mode suara")
    ap.add_argument("--demo", action="store_true", help="pratinjau island tanpa mikrofon/model/API")
    ap.add_argument("--no-voice", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--media-on-demand", action="store_true", default=None, help="media/audio hanya saat tab Media dibuka")
    ap.add_argument("--reduced-motion", action="store_true", help="kurangi gerakan island")
    args = ap.parse_args()
    if args.no_voice and not args.island:
        ap.error("--no-voice memerlukan --island")
    if (args.island or args.demo) and (args.login or args.text is not None):
        ap.error("mode island tidak digabung dengan --text atau --login")
    if args.reduced_motion and not (args.island or args.demo):
        ap.error("--reduced-motion memerlukan --island atau --demo")
    if args.login or args.text is not None:
        events.subscribe(console)

    if args.login:
        print(actions.sp().current_user()["display_name"], "- login berhasil")
        return
    if args.text:
        handle_text(args.text, args.dry)
        return

    from island import run_island
    return run_island(demo=args.demo, reduced_motion=args.reduced_motion,
                      media_on_demand=args.media_on_demand)


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
