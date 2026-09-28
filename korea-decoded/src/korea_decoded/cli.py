"""Command line entry point: python -m korea_decoded <command>."""

from __future__ import annotations

import argparse
import os
import sys

from korea_decoded import db, pipeline
from korea_decoded.collectors import NaverNewsCollector, RedditCollector, RssCollector
from korea_decoded.config import DATA_DIR, OUTPUT_DIR, load_config

DB_PATH = DATA_DIR / "korea_decoded.db"


def cmd_collect(args, conn, config) -> int:
    collectors = []
    if "reddit" in args.sources:
        ua = os.environ.get("REDDIT_USER_AGENT", "korea-decoded-collector/0.1")
        collectors.append(RedditCollector(list(config.reddit_subreddits), ua, config.reddit_timeframe))
    if "rss" in args.sources:
        collectors.append(RssCollector(list(config.rss_feeds)))
    if "naver" in args.sources:
        cid, secret = os.environ.get("NAVER_CLIENT_ID"), os.environ.get("NAVER_CLIENT_SECRET")
        if cid and secret:
            collectors.append(NaverNewsCollector(list(config.naver_queries), cid, secret))
        else:
            print("naver: skipped (NAVER_CLIENT_ID / NAVER_CLIENT_SECRET not set)")

    failed = False
    for collector in collectors:
        name = type(collector).__name__
        try:
            topics = collector.collect()
        except Exception as e:  # one broken source shouldn't stop the others
            print(f"{name}: failed ({e})", file=sys.stderr)
            failed = True
            continue
        counts = pipeline.ingest(conn, topics, config)
        print(f"{name}: {counts['new']} new, {counts['review']} ⚠️ review, "
              f"{counts['duplicate']} already collected")
    return 1 if failed else 0


def cmd_topics(args, conn, config) -> int:
    rows = db.list_topics(conn, args.status, args.limit)
    for r in rows:
        flag = "⚠️ " if r["sensitivity"] == "review" else "🟢"
        print(f"{flag} {r['uid']}  [{r['status']:<8}] {r['score']:>5.2f}  "
              f"{(r['pillar'] or '-'):<14} {r['title'][:80]}")
    if not rows:
        print("(no topics)")
    return 0


def cmd_review(args, conn, config) -> int:
    rows = db.list_topics(conn, "review", args.limit)
    if not rows:
        print("⚠️ review queue is empty")
    for r in rows:
        print(f"⚠️ {r['uid']}  {r['title']}")
        print(f"    reason: {r['sensitivity_reason']}")
        print(f"    source: {r['url']}")
        if r["script_path"]:
            print(f"    draft:  {r['script_path']}")
    return 0


def cmd_decide(args, conn, config) -> int:
    row = conn.execute("SELECT * FROM topics WHERE uid = ?", (args.uid,)).fetchone()
    if row is None:
        print(f"unknown topic: {args.uid}", file=sys.stderr)
        return 1
    if args.command == "reject":
        status = "rejected"
    else:
        # Keep an existing draft instead of paying to regenerate it.
        status = "scripted" if row["script_path"] and not args.rewrite else "approved"
    db.set_status(conn, args.uid, status)
    print(f"{args.uid} -> {status}")
    return 0


def cmd_write(args, conn, config) -> int:
    from korea_decoded.scriptwriter import ScriptWriter, build_system_prompt, build_user_message

    if args.dry_run:
        print(build_system_prompt(config))
        for topic in db.ready_for_script(conn, args.limit):
            print("\n=== USER ===\n" + build_user_message(topic))
        return 0
    writer = ScriptWriter(config)
    for uid, path, status in pipeline.write_scripts(conn, writer, OUTPUT_DIR / "scripts", args.limit):
        mark = "⚠️ flagged by model, moved to review" if status == "review" else "🟢"
        print(f"{mark} {uid} -> {path}")
    return 0


def cmd_voice(args, conn, config) -> int:
    from korea_decoded.tts import TTSError, build_tts

    failed = False
    for uid in args.uids:
        try:
            voice, path = pipeline.voice_topic(conn, uid, config, OUTPUT_DIR / "audio", build_tts, args.voice)
        except (pipeline.PipelineError, TTSError) as e:
            print(f"{uid}: {e}", file=sys.stderr)
            failed = True
            continue
        print(f"🎙️ {uid} [{voice}] -> {path}")
    return 1 if failed else 0


def cmd_visuals(args, conn, config) -> int:
    from korea_decoded import visuals
    from korea_decoded.config import PROJECT_ROOT

    sources = visuals.build_sources(config)
    if not sources:
        print("no PEXELS_API_KEY and AI images disabled: every scene will be a text card")
    font = PROJECT_ROOT / config.editor.get("font_path", "assets/fonts/Montserrat-ExtraBold.ttf")
    failed = False
    for uid in args.uids:
        try:
            paths, credits = pipeline.visuals_topic(conn, uid, OUTPUT_DIR / "visuals",
                                                    visuals.VisualPlanner(), sources, font)
        except Exception as e:
            print(f"{uid}: {e}", file=sys.stderr)
            failed = True
            continue
        counts = {s: sum(c.source == s for c in credits) for s in ("stock", "ai", "card")}
        print(f"🖼️ {uid}: {len(paths)} images (stock {counts['stock']}, ai {counts['ai']}, "
              f"card {counts['card']}) -> {OUTPUT_DIR / 'visuals' / uid}")
    return 1 if failed else 0


def cmd_render(args, conn, config) -> int:
    from pathlib import Path

    from korea_decoded import editor
    from korea_decoded.visuals import existing_images

    folder = Path(args.images) if args.images else OUTPUT_DIR / "visuals" / args.uid
    images = existing_images(folder)
    if not images:
        print(f"no images in {folder} (run `visuals {args.uid}` or pass --images)", file=sys.stderr)
        return 1
    model = config.editor.get("whisper_model", "base.en")
    try:
        path = pipeline.render_topic(conn, args.uid, images, OUTPUT_DIR / "video", config,
                                     transcribe=lambda audio: editor.transcribe(audio, model),
                                     render=editor.render)
    except pipeline.PipelineError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"🎬 {args.uid} -> {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="korea_decoded", description="Four Eyes Report pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("collect", help="fetch topics from sources")
    p.add_argument("--sources", nargs="+", default=["reddit", "rss", "naver"],
                   choices=["reddit", "rss", "naver"])
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("topics", help="list collected topics by score")
    p.add_argument("--status", choices=db.STATUSES)
    p.add_argument("--limit", type=int, default=30)
    p.set_defaults(func=cmd_topics)

    p = sub.add_parser("review", help="show the ⚠️ review queue")
    p.add_argument("--limit", type=int, default=30)
    p.set_defaults(func=cmd_review)

    for name in ("approve", "reject"):
        p = sub.add_parser(name, help=f"{name} a review topic")
        p.add_argument("uid")
        p.add_argument("--rewrite", action="store_true",
                       help="approve: regenerate the script even if a draft exists")
        p.set_defaults(func=cmd_decide)

    p = sub.add_parser("write", help="generate scripts for the top ready topics")
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--dry-run", action="store_true", help="print the prompts without calling the API")
    p.set_defaults(func=cmd_write)

    p = sub.add_parser("voice", help="narrate fact-checked scripts (voice picked by pillar)")
    p.add_argument("uids", nargs="+")
    p.add_argument("--voice", help="override the pillar's voice, e.g. skye / miles / fenrir")
    p.set_defaults(func=cmd_voice)

    p = sub.add_parser("visuals", help="find one background image per script line")
    p.add_argument("uids", nargs="+")
    p.set_defaults(func=cmd_visuals)

    p = sub.add_parser("render", help="render a narrated topic into a vertical Short")
    p.add_argument("uid")
    p.add_argument("--images", help="folder of background images in name order "
                   "(default: the folder `visuals` filled)")
    p.set_defaults(func=cmd_render)

    args = parser.parse_args(argv)
    config = load_config()
    conn = db.connect(DB_PATH)
    try:
        return args.func(args, conn, config)
    finally:
        conn.close()
