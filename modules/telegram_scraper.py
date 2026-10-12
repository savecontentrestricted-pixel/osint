"""
Advanced Telegram Channel Scraper - OSINT Tool 1
Uses Telethon MTProto client to scrape max public data.

Features:
- Channel info + full metadata
- Message scraping with limit, offset, date range
- Media filtering
- Keyword search inside channel
- Stats + Top posts
- Export JSON/CSV/Excel
- FloodWait handling + rate limiting
- Batch scraping
"""

import asyncio
import re
import json
import csv
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Channel, Chat, User
from telethon.errors import FloodWaitError, ChannelPrivateError, UsernameInvalidError, UsernameNotOccupiedError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest

class TelegramScraper:
    def __init__(self, api_id: int, api_hash: str, session_string: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_string = session_string
        self.client: Optional[TelegramClient] = None

    async def _get_client(self) -> TelegramClient:
        if self.client and self.client.is_connected():
            return self.client
        self.client = TelegramClient(StringSession(self.session_string), self.api_id, self.api_hash)
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise Exception("Session expired / not authorized. generate_session.py dobara chalao.")
        return self.client

    async def close(self):
        if self.client:
            try:
                await self.client.disconnect()
            except:
                pass

    def _clean_channel_input(self, inp: str) -> str:
        inp = inp.strip()
        # Remove t.me/ prefix
        inp = re.sub(r'^https?://t\.me/', '', inp, flags=re.I)
        inp = re.sub(r'^t\.me/', '', inp, flags=re.I)
        inp = inp.lstrip('@')
        # If link like channel/123, keep as is for ID based
        if '/' in inp:
            # take first part as username, second as msg id maybe
            parts = inp.split('/')
            return parts[0]
        return inp

    async def get_channel_info(self, channel_input: str) -> Dict[str, Any]:
        client = await self._get_client()
        clean = self._clean_channel_input(channel_input)
        
        try:
            entity = await client.get_entity(clean)
        except (UsernameInvalidError, UsernameNotOccupiedError) as e:
            return {"ok": False, "error": f"Channel not found: {clean} - {str(e)}"}
        except ChannelPrivateError:
            return {"ok": False, "error": f"Channel private hai ya aap member nahi ho: {clean}"}
        except Exception as e:
            return {"ok": False, "error": f"Error: {str(e)}"}

        try:
            full = None
            if isinstance(entity, Channel):
                try:
                    full = await client(GetFullChannelRequest(entity))
                except:
                    pass

            info = {
                "ok": True,
                "id": getattr(entity, 'id', None),
                "title": getattr(entity, 'title', None) or getattr(entity, 'first_name', ''),
                "username": getattr(entity, 'username', None),
                "type": "Channel" if isinstance(entity, Channel) else "Chat" if isinstance(entity, Chat) else "User",
                "is_broadcast": getattr(entity, 'broadcast', False) if isinstance(entity, Channel) else False,
                "is_megagroup": getattr(entity, 'megagroup', False) if isinstance(entity, Channel) else False,
                "participants_count": getattr(full.full_chat, 'participants_count', None) if full and hasattr(full, 'full_chat') else getattr(entity, 'participants_count', None),
                "online_count": getattr(full.full_chat, 'online_count', None) if full and hasattr(full, 'full_chat') else None,
                "description": getattr(full.full_chat, 'about', '') if full and hasattr(full.full_chat, 'about') else '',
                "creation_date": getattr(entity, 'date', None).isoformat() if getattr(entity, 'date', None) else None,
                "is_verified": getattr(entity, 'verified', False),
                "is_restricted": getattr(entity, 'restricted', False),
                "is_scam": getattr(entity, 'scam', False),
                "is_fake": getattr(entity, 'fake', False),
                "access_hash": getattr(entity, 'access_hash', None),
            }
            return info
        except Exception as e:
            return {"ok": False, "error": f"Info parse error: {str(e)}"}

    async def scrape_messages(
        self,
        channel_input: str,
        limit: int = 100,
        offset_id: int = 0,
        min_id: int = 0,
        max_id: int = 0,
        search_query: Optional[str] = None,
        media_only: bool = False,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Advanced scraping with filters
        Returns dict with messages list + stats
        """
        client = await self._get_client()
        clean = self._clean_channel_input(channel_input)
        limit = max(1, min(limit, 10000))  # max 10k per request

        try:
            entity = await client.get_entity(clean)
        except Exception as e:
            return {"ok": False, "error": f"Channel resolve fail: {str(e)}"}

        messages_data = []
        total_views = 0
        total_forwards = 0
        media_count = 0
        link_count = 0
        hashtag_count = 0
        mention_count = 0

        try:
            # Use iter_messages with flood handling
            iter_kwargs = {
                "entity": entity,
                "limit": limit,
                "offset_id": offset_id,
                "min_id": min_id,
                "max_id": max_id,
                "search": search_query,
            }
            if date_from:
                iter_kwargs["offset_date"] = date_to  # telethon uses offset_date as upper bound
                # We'll filter manually for date_from
            # Remove None values
            iter_kwargs = {k: v for k, v in iter_kwargs.items() if v not in (None, 0, "") or k in ("offset_id", "min_id", "max_id")}

            async for msg in client.iter_messages(**iter_kwargs):
                # Date filters
                if date_from and msg.date:
                    # msg.date is aware
                    msg_date = msg.date
                    if msg_date.tzinfo is None:
                        msg_date = msg_date.replace(tzinfo=timezone.utc)
                    if date_from.tzinfo is None:
                        df = date_from.replace(tzinfo=timezone.utc)
                    else:
                        df = date_from
                    if msg_date < df:
                        continue
                if date_to and msg.date:
                    msg_date = msg.date
                    if msg_date.tzinfo is None:
                        msg_date = msg_date.replace(tzinfo=timezone.utc)
                    if date_to.tzinfo is None:
                        dt = date_to.replace(tzinfo=timezone.utc)
                    else:
                        dt = date_to
                    if msg_date > dt:
                        continue

                # Media only filter
                if media_only and not msg.media:
                    continue

                # Build message data - max info
                text = msg.text or msg.message or ""
                # Extract entities
                links = re.findall(r'https?://\S+', text)
                hashtags = re.findall(r'#\w+', text)
                mentions = re.findall(r'@\w+', text)

                # Media info
                media_info = None
                if msg.media:
                    media_count += 1
                    try:
                        media_type = type(msg.media).__name__
                        # Try to get file name/size if document
                        file_name = None
                        file_size = None
                        if hasattr(msg.media, 'document'):
                            doc = msg.media.document
                            file_size = getattr(doc, 'size', None)
                            for attr in getattr(doc, 'attributes', []):
                                if hasattr(attr, 'file_name'):
                                    file_name = attr.file_name
                                    break
                        media_info = {
                            "type": media_type,
                            "file_name": file_name,
                            "file_size": file_size,
                        }
                    except:
                        media_info = {"type": type(msg.media).__name__}

                if links:
                    link_count += len(links)
                if hashtags:
                    hashtag_count += len(hashtags)
                if mentions:
                    mention_count += len(mentions)

                views = getattr(msg, 'views', 0) or 0
                forwards = getattr(msg, 'forwards', 0) or 0
                total_views += views
                total_forwards += forwards

                # Reactions
                reactions = []
                try:
                    if msg.reactions and hasattr(msg.reactions, 'results'):
                        for r in msg.reactions.results:
                            reactions.append({
                                "emoji": getattr(r.reaction, 'emoticon', str(r.reaction)) if hasattr(r, 'reaction') else str(r),
                                "count": getattr(r, 'count', 0)
                            })
                except:
                    pass

                msg_data = {
                    "id": msg.id,
                    "date": msg.date.isoformat() if msg.date else None,
                    "text": text[:4000],  # limit for export
                    "text_full": text,  # full for json
                    "views": views,
                    "forwards": forwards,
                    "replies": getattr(msg, 'replies', None).replies if getattr(msg, 'replies', None) else 0,
                    "is_media": bool(msg.media),
                    "media": media_info,
                    "links": links,
                    "hashtags": hashtags,
                    "mentions": mentions,
                    "reactions": reactions,
                    "link": f"https://t.me/{getattr(entity, 'username', clean)}/{msg.id}" if getattr(entity, 'username', None) else f"ID:{msg.id}",
                    "from_id": getattr(msg.from_id, 'user_id', None) if msg.from_id else None,
                }
                messages_data.append(msg_data)

                # Small delay to avoid flood (every 50 msgs)
                if len(messages_data) % 50 == 0:
                    await asyncio.sleep(0.5)

        except FloodWaitError as e:
            # Return partial data + wait info
            return {
                "ok": True,
                "partial": True,
                "flood_wait": e.seconds,
                "messages": messages_data,
                "stats": {
                    "scraped": len(messages_data),
                    "total_views": total_views,
                    "total_forwards": total_forwards,
                    "media_count": media_count,
                    "link_count": link_count,
                },
                "warning": f"FloodWait {e.seconds}s - partial data returned. Thoda wait karke dobara try karo."
            }
        except Exception as e:
            return {"ok": False, "error": f"Scrape error: {str(e)}", "messages": messages_data}

        # Stats
        avg_views = total_views // len(messages_data) if messages_data else 0
        top_posts = sorted(messages_data, key=lambda x: x['views'], reverse=True)[:10]

        return {
            "ok": True,
            "channel": clean,
            "scraped": len(messages_data),
            "messages": messages_data,
            "stats": {
                "total": len(messages_data),
                "total_views": total_views,
                "avg_views": avg_views,
                "total_forwards": total_forwards,
                "media_count": media_count,
                "media_ratio": round(media_count / len(messages_data) * 100, 2) if messages_data else 0,
                "link_count": link_count,
                "hashtag_count": hashtag_count,
                "mention_count": mention_count,
                "top_posts": top_posts,
            }
        }

    def export_json(self, data: Dict, filepath: str):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_csv(self, messages: List[Dict], filepath: str):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        if not messages:
            return
        # Flatten for CSV
        fieldnames = ["id", "date", "text", "views", "forwards", "replies", "is_media", "media_type", "link", "links", "hashtags", "mentions"]
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for m in messages:
                writer.writerow({
                    "id": m.get("id"),
                    "date": m.get("date"),
                    "text": (m.get("text") or "")[:1000].replace("\n", " "),
                    "views": m.get("views"),
                    "forwards": m.get("forwards"),
                    "replies": m.get("replies"),
                    "is_media": m.get("is_media"),
                    "media_type": (m.get("media") or {}).get("type") if m.get("media") else "",
                    "link": m.get("link"),
                    "links": ", ".join(m.get("links") or []),
                    "hashtags": ", ".join(m.get("hashtags") or []),
                    "mentions": ", ".join(m.get("mentions") or []),
                })

    def export_txt(self, messages: List[Dict], filepath: str):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            for m in messages:
                f.write(f"ID: {m.get('id')} | Date: {m.get('date')} | Views: {m.get('views')} | Link: {m.get('link')}\n")
                f.write(f"Text: {m.get('text')}\n")
                f.write("-"*80 + "\n")

    async def batch_scrape(self, channels: List[str], limit_per_channel: int = 100) -> Dict[str, Any]:
        results = {}
        for ch in channels[:5]:  # max 5 at once
            try:
                res = await self.scrape_messages(ch, limit=limit_per_channel)
                results[ch] = res
                await asyncio.sleep(2)  # delay between channels
            except Exception as e:
                results[ch] = {"ok": False, "error": str(e)}
        return results
