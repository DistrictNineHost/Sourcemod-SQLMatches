# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2020 WardPearce
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.requests import Request

from webargs import fields
from webargs_starlette import use_args

from .rate_limiter import LIMITER

from ...community import create_community
from ...community.exceptions import InvalidCommunity

from ...api import response
from ...api.model_convertor import community_to_dict


class CommunityOwnerAPI(HTTPEndpoint):
    @requires("is_owner")
    @LIMITER.limit("20/minute")
    async def get(self, request: Request) -> response:
        """Gets community details including secrets.

        Parameters
        ----------
        request : Request
        """

        try:
            community = await request.state.community.get()
        except InvalidCommunity:
            raise
        else:
            return response(community_to_dict(community))

    @requires("is_owner")
    @LIMITER.limit("1/minute")
    async def delete(self, request: Request) -> response:
        """Used to disable a community.

        Parameters
        ----------
        request : Request
        """

        await request.state.community.disable()

        return response()

    @requires("is_owner")
    @LIMITER.limit("10/minute")
    async def post(self, request: Request) -> response:
        """Used to regenerate a key for a community.

        Parameters
        ----------
        request : Request
        """

        return response({
            "master_api_key": await request.state.community.regenerate_master()
        })


class CommunityAPI(HTTPEndpoint):
    @use_args({"community_name": fields.Str(required=True),
              "demos": fields.Bool()})
    @requires("steam_login")
    @LIMITER.limit("10/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to create a community.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        community, _ = await create_community(
            steam_id=request.session["steam_id"],
            **parameters
        )

        return response(community_to_dict(community))
