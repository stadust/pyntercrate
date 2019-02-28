from .model import *

from aiohttp import ClientSession

from typing import List

import re
from urllib.parse import urlparse, parse_qs


class _Unmodified(object):
    pass


Unmodified = _Unmodified()


class PointercrateClient(object):
    def __init__(self, token=None, *, api_base="https://pointercrate.com/api/v1/"):
        self.api_base = api_base
        self.token = token
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.token is not None:
            headers['Authorization'] = f'Bearer {self.token}'

        self.session = ClientSession(headers=headers)

    async def _resp(self, resp):
        if resp.status < 400:
            return await resp.json()
        else:
            raise ApiException(**(await resp.json()))

    async def _pagination_resp(self, resp):
        data = await self._resp(resp)

        pagination_data = dict()

        for link in resp.headers['Links'].split(','):
            url, ident = link.split(';')
            print(ident, url)
            pagination_data[ident[5:]] = {k: v[0]
                                          for k, v in parse_qs(urlparse(url[1:-1]).query).items()}

        return data, pagination_data

    async def me(self):
        async with self.session.get(f"{self.api_base}auth/me/") as resp:
            data = await self._resp(resp)

            return User(resp.headers['etag'], **data['data'])

    async def demons(self, *, limit: int = None, after: int = None, before: int = None, name: str = None, requirement: int = None, min_requirement: int = None, max_requirement: int = None):
        params = de_none({
            "limit": limit,
            "after": after,
            "before": before,
            "name": name,
            "requirement": requirement,
            "requirement__gt": None if min_requirement is None else min_requirement - 1,
            "requirement__lt": None if max_requirement is None else max_requirement + 1
        })

        async with self.session.get(self.api_base + "demons/", params=params) as resp:
            data, pagination_data = await self._pagination_resp(resp)

            return [ShortDemon(**demon) for demon in data], pagination_data

    async def demon_at(self, position: int):
        async with self.session.get(f"{self.api_base}demons/{position}/") as resp:
            data = await self._resp(resp)

            return Demon(resp.headers['etag'], **data['data'])

    async def add_demon(self, name: str, position: int, requirement: int, verifier: str, publisher: str, creators: List[str], video: str = None):
        json = {
            "name": name,
            "position": position,
            "requirement": requirement,
            "verifier": verifier,
            "publisher": publisher,
            "creators": creators,
            "video": video
        }

        async with self.session.post(self.api_base + "demons/", json=json) as resp:
            data = await self._resp(resp)

            return Demon(resp.headers['etag'], **data['data'])

    async def patch_demon(self, demon: Demon, *, name: str = Unmodified, position: int = Unmodified, video: str = Unmodified, requirement: int = Unmodified, verifier: str = Unmodified, publisher: str = Unmodified):
        headers = {
            'If-Match': demon.etag
        }

        json = de_unmod({
            'name': name,
            'position': position,
            'video': video,
            'requirement': requirement,
            'verifier': verifier,
            'publisher': publisher
        })

        async with self.session.patch(f"{self.api_base}demons/{demon.position}/", json=json, headers=headers) as resp:
            data = await self._resp(resp)

            return Demon(resp.headers['etag'], **data['data'])

    async def add_creator(self, demon: Demon, creator: str):
        json = {
            "creator": creator
        }

        async with self.session.post(f"{self.api_base}demons/{demon.position}/creators/", json=json) as resp:
            if resp.status >= 400:
                raise ApiException(**(await resp.json()))

    async def remove_creator(self, demon: Demon, creator: Player):
        async with self.session.delete(f"{self.api_base}demons/{demon.position}/creators/{creator.id}/") as resp:
            if resp.status >= 400:
                raise ApiException(**(await resp.json()))

    async def players(self, *, limit: int = None, after: int = None, before: int = None, name: str = None, banned: bool = None):
        params = de_none({
            "limit": limit,
            "after": after,
            "before": before,
            "name": name,
            "banned": banned
        })

        async with self.session.get(self.api_base + "players/", params=params) as resp:
            data, pagination_data = await self._pagination_resp(resp)

            return [ShortPlayer(**player) for player in data], pagination_data

    async def get_player(self, pid: int):
        async with self.session.get(f"{self.api_base}players/{pid}/") as resp:
            data = await self._resp(resp)

            return Player(resp.headers['etag'], **data['data'])

    async def patch_player(self, player: Player, *, banned: bool = Unmodified):
        headers = {
            'If-Match': player.etag
        }

        json = de_unmod({
            'banned': banned,
        })

        async with self.session.patch(f"{self.api_base}demons/{player.id}/", json=json, headers=headers) as resp:
            data = await self._resp(resp)

            return Player(resp.headers['etag'], **data['data'])

    async def records(self, *, limit: int = None, after: int = None, before: int = None, progress: int = None, min_progress: int = None, max_progress: int = None, status: str = None, player: str = None, demon: str = None):
        params = de_none({
            "limit": limit,
            "after": after,
            "before": before,
            "status": status,
            "progress": progress,
            "progress__gt": None if min_progress is None else min_progress - 1,
            "progress__lt": None if max_progress is None else max_progress + 1,
            "player": player,
            "demon": demon
        })

        async with self.session.get(self.api_base + "records/", params=params) as resp:
            data, pagination_data = await self._pagination_resp(resp)

            return [ShortRecord(**record) for record in data], pagination_data

    async def get_record(self, rid: int):
        async with self.session.get(f"{self.api_base}records/{rid}/") as resp:
            data = await self._resp(resp)

            return Record(resp.headers['etag'], **data['data'])

    async def add_record(self, progress: int, player: str, demon: str, status: str = 'submitted', video: str = None):
        json = {
            "progress": progress,
            "player": player,
            "demon": demon,
            "status": status,
            "video": video,
        }

        async with self.session.post(self.api_base + "records/", json=json) as resp:
            data = await self._resp(resp)

            return Record(resp.headers['etag'], **data['data'])

    async def patch_record(self, record: Record, *, progress: int = Unmodified, video: str = Unmodified, status: str = Unmodified, player: str = Unmodified, demon: str = Unmodified):
        headers = {
            'If-Match': record.etag
        }

        json = de_unmod({
            'progress': progress,
            'video': video,
            'status': status,
            'player': player,
            'demon': demon,
        })

        async with self.session.patch(f"{self.api_base}records/{record.id}/", json=json, headers=headers) as resp:
            data = await self._resp(resp)

            return Record(resp.headers['etag'], **data['data'])

    async def delete_record(self, record: Record):
        headers = {
            'If-Match': record.etag
        }
        async with self.session.delete(f"{self.api_base}records/{record.id}/", headers=headers) as resp:
            if resp.status >= 400:
                raise ApiException(**(await resp.json()))

    async def submitters(self, *, limit: int = None, after: int = None, before: int = None, banned: bool = None):
        params = de_none({
            "limit": limit,
            "after": after,
            "before": before,
            "banned": banned,
        })

        async with self.session.get(self.api_base + "submitters/", params=params) as resp:
            data, pagination_data = await self._pagination_resp(resp)

            return [ShortSubmitter(**submitter) for submitter in data], pagination_data

    async def get_submitter(self, sid: int):
        async with self.session.get(f"{self.api_base}submitters/{sid}/") as resp:
            data = await self._resp(resp)

            return Submitter(resp.headers['etag'], **data['data'])

    async def patch_submitter(self, submitter: Submitter, *, banned: bool = Unmodified):
        headers = {
            'If-Match': submitter.etag
        }

        json = de_unmod({
            'banned': banned
        })

        async with self.session.patch(f"{self.api_base}submitters/{submitter.id}/", json=json, headers=headers) as resp:
            data = await self._resp(resp)

            return Submitter(resp.headers['etag'], **data['data'])

    async def close(self):
        await self.session.close()


def de_none(d):
    return {k: v for k, v in d.items() if v is not None}


def de_unmod(d):
    return {k: v for k, v in d.items() if v is not Unmodified}
