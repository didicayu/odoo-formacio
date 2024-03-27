from odoo import models, fields, api
from passlib.context import CryptContext
from datetime import datetime
import binascii
import os

# API keys support
API_KEY_SIZE = 20  # in bytes
INDEX_SIZE = 8  # in hex digits, so 4 bytes, or 20% of the key
KEY_CRYPT_CONTEXT = CryptContext(
    # default is 29000 rounds which is 25~50ms, which is probably unnecessary
    # given in this case all the keys are completely random data: dictionary
    # attacks on API keys isn't much of a concern
    ['pbkdf2_sha512'], pbkdf2_sha512__rounds=6000,
)


class ApiKeyUserMixin(models.AbstractModel):
    _name = 'api.key.user.mixin'

    def generate_api_key(self, scope, name, user_id=None):
        """Generates an api key for a desired user.
        :param str scope: the scope of the key. If None, the key will give access to any rpc.
        :param str name: the name of the key, mainly intended to be displayed in the UI.
        :param user_id: the ID of the user linked to the newly generated API key
        :return: str: the key.

        """
        table = self.env['res.users.apikeys']._table

        k = binascii.hexlify(os.urandom(API_KEY_SIZE)).decode()
        print(k)

        # FIXME Aixo pot generar un problema on la taula no estigui creada perque encara no s'ha cridat el init de
        #  res.users.apikeys
        self.env.cr.execute("""
                INSERT INTO {table} (name, user_id, scope, key, index)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """.format(table=table),
                            [name, user_id, scope, KEY_CRYPT_CONTEXT.hash(k), k[:INDEX_SIZE]])

        print(f"API key generated: scope: {scope} for '{user_id}' with name: {name}")

        # FIXME otra alternativa seria dejar que super() llene los valores de la tabla y solo modificar lo que nos
        #  interese, el problema esta en los logs que no coincidirian y probablemente otras cosas importantes. otro
        #  problema seria el recuperar la key, se puede obtener del return de super() pero despues se guarda el hash

        return k

        # api_key_vals = {
        #     'name': name,
        #     'user_id': user_id or self.env.user.id,
        #     'scope': scope,
        #     'create_date': datetime.now()  # (Crec que no cal pq hi ha una querry SQL que ho fa automatic)
        # }
