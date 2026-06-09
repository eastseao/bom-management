#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""版本管理模块"""

__version__ = "1.0.0"
__version_date__ = "2026-06-09"
GITHUB_RELEASES_URL = "https://github.com/eastseao/bom-management/releases"


def check_for_updates_async(callback, force=False):
    """后台检查 GitHub 是否有新版本（简化版）"""
    import threading
    import urllib.request
    import json

    def _check():
        result = {
            "has_update": False,
            "current_version": __version__,
            "latest_version": __version__,
            "release_notes": "",
            "download_url": GITHUB_RELEASES_URL,
        }
        try:
            api_url = "https://api.github.com/repos/eastseao/bom-management/releases/latest"
            req = urllib.request.Request(api_url, headers={"User-Agent": "BOM-Management"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
                latest_tag = data.get("tag_name", "").lstrip("vV")
                if latest_tag and latest_tag != __version__:
                    result["has_update"] = True
                    result["latest_version"] = latest_tag
                    result["release_notes"] = data.get("body", "")
                    result["download_url"] = data.get("html_url", GITHUB_RELEASES_URL)
        except Exception:
            pass
        callback(result)

    threading.Thread(target=_check, daemon=True).start()
