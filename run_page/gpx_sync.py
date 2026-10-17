#!/usr/bin/env python3
"""
If you do not want bind any account
Only the gpx files in GPX_OUT sync
"""

import argparse

from config import GPX_FOLDER, JSON_FILE, SQL_FILE

from utils import make_activities_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync GPX files in GPX_OUT")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Stop after this many tracks. Omit it to sync every file.",
    )
    args = parser.parse_args()
    print("only sync gpx files in GPX_OUT")
    make_activities_file(SQL_FILE, GPX_FOLDER, JSON_FILE, limit=args.limit)
