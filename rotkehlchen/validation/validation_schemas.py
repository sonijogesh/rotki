from typing import Any, Dict, Union

from marshmallow import Schema, fields, post_load

from rotkehlchen.api.v1.schemas import UnderlyingTokenInfoSchema
from rotkehlchen.assets.asset import EthereumToken, UnderlyingToken
from rotkehlchen.assets.typing import AssetType


class AssetListSchema(Schema):
    identifier = fields.String(required=True)
    name = fields.String(required=True)
    symbol = fields.String(required=True)
    asset_type = fields.String(required=True)
    forked = fields.String(required=True, allow_none=True)
    swapped_for = fields.String(required=True, allow_none=True)
    cryptocompare = fields.String(required=True, allow_none=True)
    coingecko = fields.String(required=True, allow_none=True)
    ethereum_address = fields.String()
    decimals = fields.Integer()
    protocol = fields.String(allow_none=True)
    underlying_tokens = fields.List(fields.Nested(UnderlyingTokenInfoSchema), allow_none=True)
    started = fields.Integer(required=True, allow_none=True)

    @post_load
    def transform_data(  # pylint: disable=no-self-use
            self,
            data: Dict[str, Any],
            **_kwargs: Any,
    ) -> Dict[str, Any]:
        """Returns the a dictionary with:
        - The identifier
        - extra_information used by the globaldb handler
        - name
        - symbol
        - asset_type as instance of AssetType
        """
        given_underlying_tokens = data.pop('underlying_tokens', None)
        underlying_tokens = None
        if given_underlying_tokens is not None:
            underlying_tokens = []
            for entry in given_underlying_tokens:
                underlying_tokens.append(UnderlyingToken(
                    address=entry['address'],
                    weight=entry['weight'],
                ))

        asset_type = AssetType.deserialize_from_db(data['asset_type'])
        extra_information: Union[Dict[str, Any], EthereumToken]
        if asset_type == AssetType.ETHEREUM_TOKEN:
            extra_information = EthereumToken.initialize(
                address=data.pop('ethereum_address'),
                name=data.get('name'),
                symbol=data.get('symbol'),
                decimals=data.pop('decimals'),
                started=data.pop('started'),
                swapped_for=data.pop('swapped_for'),
                coingecko=data.pop('coingecko'),
                cryptocompare=data.pop('cryptocompare'),
                underlying_tokens=underlying_tokens,
            )
        else:
            extra_information = {
                'name': data.get('name'),
                'symbol': data.get('symbol'),
                'started': data.pop('started'),
                'swapper_for': data.pop('swapped_for'),
                'coingecko': data.pop('coingecko'),
                'cryptocompare': data.pop('cryptocompare'),
            }

        data['underlying_tokens'] = underlying_tokens
        data['asset_type'] = asset_type
        data['extra_information'] = extra_information
        return data


class ExportedAssetsSchema(Schema):
    version = fields.String(required=True)
    assets = fields.List(fields.Nested(AssetListSchema), load_default=[])
